import youtube_dl
from pydub import AudioSegment
from collections import namedtuple
import hashlib
import datetime
from os import path

from google.cloud import speech
from google.cloud import storage

TRANSCRIPTION_RESULTS = namedtuple(
    "transcription_results", ["start_time", "end_time", "transcription", "confidence"]
)
AUDIO_METADATA = namedtuple(
    "audio_metadata", ["channels", "sample_width", "frame_rate"]
)
GS_BUCKET = "scratchpad-dev-temp"


def upload_blob(bucket_name, source_file_name):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    destination_blob_name = path.basename(source_file_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    return destination_blob_name


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
        info = self.extract_url_metadata(url)
        self.extract_multimedia([url])
        downloaded_location = "/tmp/seamless_downloads/{0}-{1}.flac".format(
            info["id"], info["extractor"]
        )
        audio_metadata = self.extract_audio_metadata(downloaded_location)
        print(audio_metadata)
        gs_location = upload_blob(GS_BUCKET, downloaded_location)
        return info, gs_location, audio_metadata


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


def generate_youtube_transcript_docs(url: str, downloader_config: dict = None):
    youtube_downloader = YoutubeDLMultiMediaExtractor(config=downloader_config)
    speech_to_text = SpeechToTextWrapper()

    hash_object = hashlib.md5(str(url).encode("utf-8"))
    hash_string = hash_object.hexdigest()

    url_audio_info, url_gs_loc, url_audio_meta = youtube_downloader.extract(url)

    url_texts = speech_to_text.transcribe_file(
        speech_file=url_gs_loc, audio_metadata=url_audio_meta
    )

    # massage data to proper format
    youtube_docs = []
    for url_text in url_texts:
        print(url_text)
        meta = {
            "url": url,
            "src_ptr": hash_string,
            "src_type": "yt",
            "title": url_audio_info.get('title', url),
            "author": url_audio_info.get('author', ''),
            "start_time": str(url_text.get('start_time')),
            "end_time": str(url_text.get('end_time')),
            "confidence": url_text.get('confidence'),
        }
        yt_doc = {'content': url_text.get('transcription'), 'meta': meta, 'id_hash_keys': None}
        youtube_docs.append(yt_doc)
    return youtube_docs