import docker
import time
from haystack.document_stores import ElasticsearchDocumentStore
from scratchpad.preprocessing.pre_processing import preprocess_add_videos

#url = 'https://www.youtube.com/watch?v=q3vzVjUTBeQ'
url = 'https://www.youtube.com/watch?v=8fGjT7YPVC8'

def test_db():
    # docker run -d -p 9200:9200 -e "discovery.type=single-node" elasticsearch:7.9.2
    client = docker.from_env()
    container = client.containers.run(
        "elasticsearch:7.9.2", detach=True, ports={"9200":"9200"}, environment={"discovery.type": "single-node"} , hostname="test-docker"
    )
    # allow docker some startup time
    time.sleep(30)
    document_store = ElasticsearchDocumentStore(
        host="localhost",
        port=9200,
        username="",
        password="",
        index="document",
        similarity="cosine",
    )
    return container, document_store

#docker_container, es = test_db()

yt_dicts = preprocess_add_videos([url])

#es.write_documents(yt_dicts)
