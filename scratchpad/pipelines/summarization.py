import logging
from pathlib import Path

from haystack import Pipeline
from haystack.pipelines import RootNode
from haystack.nodes import TransformersSummarizer

from scratchpad.retrievers import get_es_retriever, get_nn_retriever
from scratchpad.rankers import get_st_ranker
from scratchpad.summarizer import get_pegasus_summarizer

from scratchpad.pipelines.semantic_search_pipeline import JoinNode, DEFAULT_CONFIG

logger = logging.getLogger(__name__)


def summarize_pipeline(document_store, config=DEFAULT_CONFIG):
    es_retriever = get_es_retriever(document_store)
    st_retriever = get_nn_retriever(document_store, config.get("ST_RETRIEVER"))
    st_ranker = get_st_ranker(config.get("RANKER"))
    summarizer = get_pegasus_summarizer()

    # Need to test if the Ranker is necessary
    p = Pipeline()
    p.add_node(component=es_retriever, name="ESRetriever", inputs=["Query"])
    p.add_node(component=st_retriever, name="STRetriever", inputs=["Query"])
    p.add_node(component=JoinNode(), name="Joiner", inputs=["ESRetriever", "STRetriever"])
    p.add_node(component=st_ranker, name="Ranker", inputs=["Joiner"])
    p.add_node(component=summarizer, name="Summarizer", inputs=["Ranker"])

    return p


def pipeline_summarize(query, pipeline, params):
    return pipeline.run(query=query, params=params)

