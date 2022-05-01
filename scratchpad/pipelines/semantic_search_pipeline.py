import logging
from pathlib import Path

from haystack import Pipeline
from haystack.pipelines import RootNode

from scratchpad.retrievers import get_es_retriever, get_nn_retriever
from scratchpad.rankers import get_st_ranker


logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "RANKER": "cross-encoder/ms-marco-MiniLM-L-6-v2",
    "ST_RETRIEVER": "sentence-transformers/all-mpnet-base-v2",
}


class JoinNode(RootNode):
    def run(self, output=None, inputs=None):
        if inputs:
            output = {}
            output['documents'] = []
            for input_dict in inputs:
                output['documents'] += input_dict["documents"]
                for k in input_dict.keys():
                    if k != 'documents':
                        output[k] = input_dict[k]
            output['node_id'] = 'Joiner'
        return output, "output"


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


def combined_search_pipeline(document_store, config=DEFAULT_CONFIG):
    es_retriever = get_es_retriever(document_store)
    st_retriever = get_nn_retriever(document_store, config.get("ST_RETRIEVER"))
    st_ranker = get_st_ranker(config.get("RANKER"))

    p = Pipeline()
    p.add_node(component=es_retriever, name="ESRetriever", inputs=["Query"])
    p.add_node(component=st_retriever, name="STRetriever", inputs=["Query"])
    p.add_node(component=JoinNode(), name="Joiner", inputs=["ESRetriever", "STRetriever"])
    p.add_node(component=st_ranker, name="Ranker", inputs=["Joiner"])

    return p


def pipeline_search(query, pipeline, params):
    return pipeline.run(query=query, params=params)
