from haystack import Pipeline

from scratchpad.retrievers import get_es_retriever, get_nn_retriever
from scratchpad.rankers import get_st_ranker


DEFAULT_CONFIG = {
    "RANKER": "cross-encoder/ms-marco-MiniLM-L-6-v2",
    "ST_RETRIEVER": "sentence-transformers/all-mpnet-base-v2",
}


def bm25_ranker_search_pipeline(document_store, config=DEFAULT_CONFIG):
    es_retriever = get_es_retriever(document_store)
    st_ranker = get_st_ranker(config.get("RANKER"))

    p = Pipeline()
    p.add_node(component=es_retriever, name="ESRetriever", inputs=["Query"])
    p.add_node(component=st_ranker, name="Ranker", inputs=["ESRetriever"])

    return p


def dense_retriever_ranker_search_pipeline(document_store, config=DEFAULT_CONFIG):
    st_retriever = get_nn_retriever(document_store, config.get("ST_RETRIEVER"))
    st_ranker = get_st_ranker(config.get("RANKER"))

    p = Pipeline()
    p.add_node(component=st_retriever, name="STRetriever", inputs=["Query"])
    p.add_node(component=st_ranker, name="Ranker", inputs=["STRetriever"])

    return p


def pipeline_search(query, pipeline, params):
    return pipeline.run(query=query, params=params)
