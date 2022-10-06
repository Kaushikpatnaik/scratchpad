import logging
from pathlib import Path
from typing import Optional, List

import os
import openai

from haystack.schema import Document
from haystack import Pipeline
from haystack.nodes.base import BaseComponent
from haystack.nodes.other import JoinDocuments

from scratchpad.retrievers import get_es_retriever, get_nn_retriever
from scratchpad.rankers import get_st_ranker

from scratchpad.pipelines.semantic_search_pipeline import DEFAULT_CONFIG

logger = logging.getLogger(__name__)
openai.api_key = "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"


class OpenAISummarize(BaseComponent):
    # If it's not a decision node, there is only one outgoing edge
    outgoing_edges = 1

    def __init__(self):
        super().__init__()
        openai.api_key = "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"

    def run(self, documents: List[Document]):
        # Insert code here to manipulate the input and produce an output dictionary
        results = []
        for doc in documents:
            response = openai.Completion.create(
                model="text-davinci-002",
                prompt=doc.content + ".\n\nTl;dr",
                temperature=0.7,
                max_tokens=100,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
            )
            response_text = response["choices"][0]["text"]
            results.append((response_text, doc.meta["file_name"]))

        output_document = (
            "\n".join([x[0] for x in results])
            + "\n\n Sources:"
            + "\n".join([x[1] for x in results])
        )

        output = {"documents": output_document, "_debug": {"prompt": documents}}
        return output, "output_1"

    def run_batch(self, documents: List[Document]):
        # Insert code here to manipulate the input and produce an output dictionary
        results = []
        for doc in documents:
            response = openai.Completion.create(
                model="text-davinci-002",
                prompt=doc.content + ".\n\nTl;dr",
                temperature=0.7,
                max_tokens=100,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
            )
            response_text = response["choices"][0]["text"]
            # remove prefix :
            response_text = response_text.replace(":", "")
            results.append((response_text, doc.meta["file_name"]))

        output_document = (
            "\n".join([x[0] for x in results])
            + "\n\n Sources: "
            + "\n".join([x[1] for x in results])
        )

        output = {"documents": output_document, "_debug": {"prompt": documents}}
        return output, "output_1"


def summarize_pipeline(document_store, config=DEFAULT_CONFIG):
    es_retriever = get_es_retriever(document_store)
    st_retriever = get_nn_retriever(document_store, config.get("ST_RETRIEVER"))
    st_ranker = get_st_ranker(config.get("RANKER"))
    join_documents = JoinDocuments(join_mode="concatenate")

    # Need to test if the Ranker is necessary
    p = Pipeline()
    p.add_node(component=es_retriever, name="ESRetriever", inputs=["Query"])
    p.add_node(component=st_retriever, name="STRetriever", inputs=["Query"])
    p.add_node(
        component=join_documents, name="Joiner", inputs=["ESRetriever", "STRetriever"]
    )
    p.add_node(component=st_ranker, name="Ranker", inputs=["Joiner"])
    p.add_node(component=OpenAISummarize(), name="Summarizer", inputs=["Ranker"])

    return p


def pipeline_summarize(query, pipeline, params):
    return pipeline.run(query=query, params=params)
