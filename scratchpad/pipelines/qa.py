import logging
from typing import Optional, List

import random
from collections import namedtuple
import openai

from datasets import load_dataset

from haystack.schema import Document
from haystack import Pipeline
from haystack.nodes.base import BaseComponent
from haystack.nodes.other import JoinDocuments
from haystack.nodes.answer_generator import OpenAIAnswerGenerator

from scratchpad.retrievers import get_es_retriever, get_nn_retriever
from scratchpad.rankers import get_st_ranker

from scratchpad.pipelines.semantic_search_pipeline import DEFAULT_CONFIG

logger = logging.getLogger(__name__)


def qa_pipeline(document_store, config=DEFAULT_CONFIG):
    es_retriever = get_es_retriever(document_store)
    st_retriever = get_nn_retriever(document_store, config.get("ST_RETRIEVER"))
    st_ranker = get_st_ranker(config.get("RANKER"))
    join_documents = JoinDocuments(join_mode="concatenate")
    generator = OpenAIAnswerGenerator(api_key = "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", model="text-davinci-002", top_k=3)

    # Need to test if the Ranker is necessary
    p = Pipeline()
    p.add_node(component=es_retriever, name="ESRetriever", inputs=["Query"])
    p.add_node(component=st_retriever, name="STRetriever", inputs=["Query"])
    p.add_node(
        component=join_documents, name="Joiner", inputs=["ESRetriever", "STRetriever"]
    )
    p.add_node(component=st_ranker, name="Ranker", inputs=["Joiner"])
    p.add_node(component=generator, name="QA", inputs=["Ranker"])

    return p


def pipeline_qa(query, pipeline, params):
    return pipeline.run(query=query, params=params)
