import docker
import time
import webvtt
import copy
from haystack.schema import Document

from haystack.document_stores import ElasticsearchDocumentStore
from scratchpad.preprocessing.pre_processing import preprocess_add_videos
from scratchpad.preprocessing.youtube_converter import YoutubeDLMultiMediaExtractor, SpeechToTextWrapper

def test_db():
    # docker run -d -p 9200:9200 -e "discovery.type=single-node" elasticsearch:7.9.2
    #client = docker.from_env()
    #container = client.containers.run(
    #    "elasticsearch:7.9.2", detach=True, ports={"9200":"9200"}, environment={"discovery.type": "single-node"} , hostname="test-docker"
    #)
    container = None
    # allow docker some startup time
    #time.sleep(30)
    document_store = ElasticsearchDocumentStore(
        host="localhost",
        port=9200,
        username="",
        password="",
        index="document",
        similarity="cosine",
    )
    return container, document_store


config = {
            "outtmpl": "/tmp/seamless_downloads/%(id)s-%(extractor)s.%(ext)s",
            "subtitleslangs": ["en"],
            "writeautomaticsub": True,
            #"writesubtitles": True,
            #"allsubtitles": True,
            "subtitlesformat": "srt",
            "skip_download": True,
            "verbose": 3
        }

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

urls = ['https://www.youtube.com/watch?v=qlB0TPBQ7YY', 'https://www.youtube.com/watch?v=ccBMRryxGog',
        'https://www.youtube.com/watch?v=0JlB9gufTw8', 'https://www.youtube.com/watch?v=AQtPoDnauq4',
        'https://www.youtube.com/watch?v=lYOG1aUzSt0', 'https://www.youtube.com/watch?v=6eOU5OaKd8s',
		'https://www.youtube.com/watch?v=y_otSD3LYCA', 'https://www.youtube.com/watch?v=UPlv-lFWITI',
	    'https://www.youtube.com/watch?v=Suhp3OLASSo', 'https://www.youtube.com/watch?v=sNfkZFVm_xs',
	    'https://www.youtube.com/watch?v=V8FEFw50lg4', 'https://www.youtube.com/watch?v=A8F4Qga3NaM']

docker_container, es = test_db()
for url in urls:
    youtube_downloader = YoutubeDLMultiMediaExtractor(config=None)
    url_audio_info, url_loc = youtube_downloader.extract(url)

    meta = {
            "url": url,
            "src_type": "yt",
            "title": url_audio_info.get('title', url),
            "author": url_audio_info.get('author', '')
        }

    youtube_docs = _cleanup_yt_subtitles(url_loc, meta)
    es.write_documents(youtube_docs)

#https://us-west2-scratchpad-348314.cloudfunctions.net/yt_parser