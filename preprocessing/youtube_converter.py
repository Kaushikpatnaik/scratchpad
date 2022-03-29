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
from urllib import request
from urllib.parse import urlparse
from collections import namedtuple
import logging
import hashlib

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import youtube_dl

from pydub import AudioSegment

from google.cloud import speech
from google.cloud import storage

from utils import upload_blob, download_blob, ReadwiseConverter


logger = logging.getLogger(__name__)

TRANSCRIPTION_RESULTS = namedtuple(
    "transcription_results", ["start_time", "end_time", "transcription", "confidence"]
)
AUDIO_METADATA = namedtuple(
    "audio_metadata", ["channels", "sample_width", "frame_rate"]
)
GS_BUCKET = "seamless-dev"


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
                "format": "bestaudio/best",
                "postprocessors": [
                    {"key": "FFmpegExtractAudio", "preferredcodec": "flac"}
                ],
            }

        self.ydl = youtube_dl.YoutubeDL(self.config)
        self.storage_client = storage.Client()

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
        info = self.extract_metadata(url)
        self.extract_multimedia([url])
        downloaded_location = "/tmp/seamless_downloads/{0}-{1}.flac".format(
            info["id"], info["extractor"]
        )
        audio_metadata = self.extract_audio_metadata(downloaded_location)
        gs_location = upload_blob(GS_BUCKET, downloaded_location)
        return info, gs_location, audio_metadata


class SpeechToTextWrapper(object):
    def __init__(self):
        self.client = speech.SpeechClient()

    def transcribe_file(self, speech_file, audio_metadata):

        uri = path.join("gs:/", GS_BUCKET, speech_file)
        audio = speech.RecognitionAudio(uri=uri)

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
            language_code="en-US",
            enable_word_time_offsets=True,
            audio_channels=audio_metadata.audio_channels,
        )

        operation = self.client.long_running_recognize(config=config, audio=audio)
        response = operation.result(timeout=90)

        transcription = []
        for result in response.results:
            alternative = result.alternatives[0]
            print("Transcript: {}".format(alternative.transcript))
            print("Confidence: {}".format(alternative.confidence))

            min_start, max_end = math.inf, 0
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


def generate_youtube_transcript_docs(url: str, downloader_config: dict = None):
    youtube_downloader = YoutubeDLMultiMediaExtractor(config=downloader_config)
    speech_to_text = SpeechToTextWrapper()
    str_converter = ReadwiseConverter()

    hash_object = hashlib.md5(str(url).encode("utf-8"))
    hash_string = hash_object.hexdigest()

    url_audio_info, url_gs_loc, url_audio_meta = youtube_downloader.extract(url)

    url_texts = speech_to_text.transcribe_file(
        speech_file=url_gs_loc, audio_metadata=url_audio_meta
    )

    # massage data to proper format
    youtube_docs = []
    for url_text in url_texts:
        url_dict = str_converter.convert(
            url.transcription,
            meta={
                "src_path": hash_string,
                "title": url_audio_info.title,
                "author": url_audio_info.author,
                "start_time": url_text.start_time,
                "end_time": url_text.end_time,
                "confidence": url_text.confidence,
            },
        )
        youtube_docs.append(url_dict)
    return youtube_docs
