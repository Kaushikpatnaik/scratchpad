import openai
import os

from haystack import Pipeline
from haystack.document_stores import ElasticsearchDocumentStore

from scratchpad.retrievers import get_es_retriever, get_nn_retriever
from scratchpad.rankers import get_st_ranker
from scratchpad.pipelines.semantic_search_pipeline import JoinNode, DEFAULT_CONFIG
from scratchpad.pipelines.summarization import OpenAISummarize

DEFAULT_CONFIG = {
    "RANKER": "cross-encoder/ms-marco-MiniLM-L-6-v2",
    "ST_RETRIEVER": "sentence-transformers/all-mpnet-base-v2"
}
DEFAULT_PARAMS = {
    "ESRetriever": {"top_k": 3},
    "STRetriever": {"top_k": 3},
    "Ranker": {"top_k": 2}
}

document_store = ElasticsearchDocumentStore(
        host="localhost",
        port=9200,
        username="",
        password="",
        index="document",
        similarity="cosine",
    )

es_retriever = get_es_retriever(document_store)
st_retriever = get_nn_retriever(document_store, DEFAULT_CONFIG.get("ST_RETRIEVER"))
st_ranker = get_st_ranker(DEFAULT_CONFIG.get("RANKER"))

# Need to test if the Ranker is necessary
p = Pipeline()
p.add_node(component=es_retriever, name="ESRetriever", inputs=["Query"])
p.add_node(component=st_retriever, name="STRetriever", inputs=["Query"])
p.add_node(component=JoinNode(), name="Joiner", inputs=["ESRetriever", "STRetriever"])
p.add_node(component=st_ranker, name="Ranker", inputs=["Joiner"])
p.add_node(component=OpenAISummarize(), name="Summarizer", inputs=["Ranker"])
result = p.run(query="cvpr", params=DEFAULT_PARAMS)
print(result)
