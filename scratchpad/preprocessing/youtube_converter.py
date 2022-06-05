"""
This file tackles extraction and download of audio/video content
from websites. The downloaded files are post-processed for information
extraction and conversion.
The following websites/embedded players are supported:
- youtube
- apple podcasts
- libsyn player
- simple audio podcasts
The extraction of websites is attempted via different methods. Firstly
we try youtube_dl program to fetch the content. If that fails we try using
headless chrome to fetch data based on xpath extraction. If all steps fails
we raise an error. This is handled as an info to the user about link not being
supported. At this stage video is converted to audio.
Post extraction, we store the downloaded file and invoke GCP functions to
perform speech to text. Any necessary pre-processing steps like audio bit-rate
and channels etc are taken care of here. 
"""

import io
import json
from os import path
import math
import datetime
from urllib import request
from urllib.parse import urlparse
from collections import namedtuple
import logging
import hashlib
import copy

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import youtube_dl
import webvtt

from pydub import AudioSegment

from google.cloud import speech
from google.cloud import storage

from haystack.schema import Document

from scratchpad.preprocessing.utils import upload_blob, download_blob


logger = logging.getLogger(__name__)

TRANSCRIPTION_RESULTS = namedtuple(
    "transcription_results", ["start_time", "end_time", "transcription", "confidence"]
)
AUDIO_METADATA = namedtuple(
    "audio_metadata", ["channels", "sample_width", "frame_rate"]
)
GS_BUCKET = "scratchpad-dev-temp"


class WebDriverMultiMediaExtractor(object):
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        self.driver = webdriver.Chrome(chrome_options=options)

    @classmethod
    def extract_multimedia(self, url):
        raise NotImplementedError

    @classmethod
    def extract_metadata(self, url):
        raise NotImplementedError


class RssWebDriverAudioExtractor(WebDriverMultiMediaExtractor):
    def __init__(self):
        super().__init__()

    def extract_multimedia(self, url):
        self.driver.get(url)
        download_link = self.driver.find_element_by_class_name(
            "download-link"
        ).get_attribute("href")
        downloaded_fileloc = "./temp.mp3"
        request.urlretrieve(download_link, downloaded_fileloc)
        return downloaded_fileloc

    def extract_metadata(self, url):
        raise NotImplementedError


# KP: Not tested
class SimpleWebDriverAudioExtractor(WebDriverMultiMediaExtractor):
    def __init__(self):
        super().__init__()

    def extract_multimedia(self, url):
        self.driver.get(url)
        self.driver.find_element_by_xpath('//*[@id="download-player"]').click()
        downloaded_fileloc = path.join("~/Downloads", path.basename(urlparse(url).path))
        return downloaded_fileloc

    def extract_metadata(self, url):
        raise NotImplementedError

    def __init__(self):
        super().__init__()

    def extract_multimedia(self, url):
        self.driver.get(url)
        self.driver.switch_to.frame(
            self.driver.find_element_by_xpath(
                '//iframestarts-with(@src, "https://html5-player.libsyn.com/embed")'
            )
        )
        self.driver.find_element_by_xpath('//*[@id="download"]').click()
        downloaded_fileloc = path.join("~/Downloads", path.basename(urlparse(url).path))
        return downloaded_fileloc

    def extract_metadata(self, url):
        raise NotImplementedError


class YoutubeDLMultiMediaExtractor(object):
    def __init__(self, config=None):
        if config:
            self.config = config
        else:
            self.config = {
            "outtmpl": "/tmp/seamless_downloads/%(id)s-%(extractor)s.%(ext)s",
            "subtitleslangs": ["en"],
            "writeautomaticsub": True,
            "subtitlesformat": "srt",
            "skip_download": True,
            "verbose": 3
        }

        self.ydl = youtube_dl.YoutubeDL(self.config)

    def extract_url_metadata(self, url):
        return self.ydl.extract_info(url, download=False)

    def extract_audio_metadata(self, fileloc):
        audio_obj = AudioSegment.from_file(fileloc)
        return AUDIO_METADATA(
            channels=audio_obj.channels,
            sample_width=audio_obj.sample_width,
            frame_rate=audio_obj.frame_rate,
        )

    def extract_multimedia(self, url):
        self.ydl.download(url)

    def extract(self, url):
        info = self.extract_url_metadata(url)
        self.extract_multimedia([url])
        downloaded_location = "/tmp/seamless_downloads/{0}-{1}.en.vtt".format(
            info["id"], info["extractor"]
        )
        return info, downloaded_location


class SpeechToTextWrapper(object):
    def __init__(self):
        self.client = speech.SpeechClient()

    def transcribe_file(self, speech_file, audio_metadata):

        uri = path.join("gs://", GS_BUCKET, speech_file)
        audio = speech.RecognitionAudio(uri=uri)

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
            language_code="en-US",
            enable_word_time_offsets=True,
            audio_channel_count=audio_metadata.channels,
        )

        operation = self.client.long_running_recognize(config=config, audio=audio)
        response = operation.result(timeout=90)

        transcription = []
        for result in response.results:
            alternative = result.alternatives[0]
            print("Transcript: {}".format(alternative.transcript))
            print("Confidence: {}".format(alternative.confidence))

            min_start, max_end = datetime.timedelta(24*60*60*60), datetime.timedelta(0)
            for word_info in alternative.words:
                start_time = word_info.start_time
                end_time = word_info.end_time
                min_start = min(min_start, start_time)
                max_end = max(max_end, end_time)

            transcription.append(
                {
                    "start_time": min_start,
                    "end_time": max_end,
                    "transcription": alternative.transcript,
                    "confidence": alternative.confidence,
                }
            )

        return transcription


def _cleanup_yt_subtitles(vtt_file, meta, batch_size=60):
    # do a first pass of the data to get caption start and end times
    # also get the complete text transcript

    docs = []
    start_times = []
    end_times = []
    subtitle_txt = None

    for caption in webvtt.read(vtt_file):
        start_times.append(caption.start)
        end_times.append(caption.end)
        if len(caption.text) > 10:
            subtitle_txt = caption.text.split("  ")
    
    start_times = start_times[:len(subtitle_txt)]
    end_times = end_times[:len(subtitle_txt)]

    batches = int(len(subtitle_txt)/batch_size)

    for it in range(batches):
        text = subtitle_txt[it*60:(it+1)*60]
        st_time = start_times[it*60:(it+1)*60]
        end_time = end_times[it*60:(it+1)*60]

        batch_strt = st_time[0]
        batch_end = end_time[-1]
        batch_text = ' '.join(text)

        caption_meta = copy.deepcopy(meta)
        caption_meta['start_time'] = batch_strt
        caption_meta['end_time'] = batch_end
        yt_doc = Document(content=batch_text, meta=caption_meta, id_hash_keys=None)
        docs.append(yt_doc)

    return docs


def generate_youtube_transcript_docs(url: str, downloader_config: dict = None):
    youtube_downloader = YoutubeDLMultiMediaExtractor(config=downloader_config)

    hash_object = hashlib.md5(str(url).encode("utf-8"))
    hash_string = hash_object.hexdigest()

    url_audio_info, url_loc = youtube_downloader.extract(url)

    meta = {
            "url": url,
            "src_type": "yt",
            "title": url_audio_info.get('title', url),
            "file_name": url_audio_info.get('title', url),
            "author": url_audio_info.get('author', '')
        }

    youtube_docs = _cleanup_yt_subtitles(url_loc, meta)
    return youtube_docs
