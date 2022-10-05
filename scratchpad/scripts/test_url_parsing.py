import logging

from haystack.document_stores import ElasticsearchDocumentStore
from scratchpad.preprocessing.pre_processing import preprocess_add_websites

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
RETRIEVER = "sentence-transformers/all-mpnet-base-v2"

document_store = ElasticsearchDocumentStore(
        host="localhost", username="", password="", index="document", similarity="cosine"
    )

urls = ["https://haystack.deepset.ai/pipeline_nodes/custom-nodes"]

url_proc_docs = preprocess_add_websites(urls)
print(url_proc_docs)