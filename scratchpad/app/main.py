"""
Server code. Support following endpoints
1. Parse website and add to db
2. Parse multimedia and add to db
3. Parse document/list of documents and ad to db
4. Neural Semantic Search
5. Click through data from users
"""

import copy
from distutils.command.config import config
import os
import uvicorn
import shutil
import logging
from pathlib import Path
from os.path import exists

from fastapi import FastAPI, UploadFile, File
from haystack.document_stores import ElasticsearchDocumentStore
from pydantic import BaseModel

from scratchpad.preprocessing.pre_processing import (
    preprocess_readwise,
    preprocess_text,
    preprocess_add_websites,
    preprocess_add_videos,
)
from scratchpad.database.write_and_update_store import write_docs_and_update_embed
from scratchpad.retrievers import get_nn_retriever
from scratchpad.pipelines.semantic_search_pipeline import (
    bm25_ranker_search_pipeline,
    dense_retriever_ranker_search_pipeline,
    pipeline_search,
    combined_search_pipeline
)
from scratchpad.pipelines.summarization import summarize_pipeline, pipeline_summarize


DEFAULT_CONFIG = {
    "RANKER": "cross-encoder/ms-marco-MiniLM-L-6-v2",
    "ST_RETRIEVER": "sentence-transformers/all-mpnet-base-v2"
}
FILE_UPLOAD_PATH = '/home/user/app/file-upload'
DEFAULT_PARAMS = {
    "ESRetriever": {"top_k": 200},
    "STRetriever": {"top_k": 200},
    "Ranker": {"top_k": 20}
}
DEFAULT_SUMM_PARAMS = {
    "ESRetriever": {"top_k": 20},
    "STRetriever": {"top_k": 20},
    "Ranker": {"top_k": 5}
}
BM25_SEARCH_PARAMS = {
    "ESRetriever": {"top_k": 200},
    "Ranker": {"top_k": 20}
}
NN_SEARCH_PARAMS = {
    "STRetriever": {"top_k": 200},
    "Ranker": {"top_k": 20}
}
os.environ["HAYSTACK_TELEMETRY_ENABLED"] = "False"


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

document_store = ElasticsearchDocumentStore(
    host="elasticsearch", username="", password="", index="document", similarity="cosine"
)
st_retriever = get_nn_retriever(document_store, DEFAULT_CONFIG.get("ST_RETRIEVER"))
#bm25_ranker = bm25_ranker_search_pipeline(document_store, config=DEFAULT_CONFIG)
#dense_ranker = dense_retriever_ranker_search_pipeline(document_store, config=DEFAULT_CONFIG)
comb_ranker = combined_search_pipeline(document_store, config=DEFAULT_CONFIG)
summarizer = summarize_pipeline(document_store, config=DEFAULT_CONFIG)


app = FastAPI()


class UrlModel(BaseModel):
    url: str
    user: str


@app.post("/parse/url")
def parse_website(data: UrlModel):
    logger.info(f"Inside parse website function in main {data}")
    url_processed_data = preprocess_add_websites([data.url], data.user)
    write_docs_and_update_embed(document_store, url_processed_data, st_retriever)


@app.post("/parse/document")
def parse_documents(docs: UploadFile = File(...), user: str = ""):
    file_path = Path(FILE_UPLOAD_PATH) / f"{docs.filename}"
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(docs.file, buffer)
    docs_processed_data = preprocess_text([str(file_path)], user)
    write_docs_and_update_embed(document_store, docs_processed_data, st_retriever)


@app.post("/parse/youtube")
def parse_youtube(data: UrlModel):
    yt_processed_data = preprocess_add_videos([data.url], data.user)
    write_docs_and_update_embed(document_store, yt_processed_data, st_retriever)


@app.get("/comb_search")
def combined_search(query: str, user: str):
    params = NN_SEARCH_PARAMS
    params["filters"] = {"user": user}
    comb_results = pipeline_search(query, comb_ranker, params=params)
    return comb_results

'''
@app.get("/bm25_search")
def bm25_search(query: str, user: str):
    params = BM25_SEARCH_PARAMS
    params["filters"] = {"user": user}
    bm25_results = pipeline_search(query, bm25_ranker, params=params)
    return bm25_results


@app.get("/nn_search")
def nn_search(query: str, user: str):
    params = DEFAULT_PARAMS
    params["filters"] = {"user": user}
    dense_results = pipeline_search(query, dense_ranker, params=params)
    return dense_results
'''

@app.get("/summarize")
def retrieval_and_summarize(query: str, user: str):
    params = DEFAULT_SUMM_PARAMS
    params["filters"] = {"user": user}
    summary_results = pipeline_summarize(query, summarizer, params=params)
    return summary_results


@app.get("/user_click_search")
def click_search_result(result: str, user: str):
    raise NotImplementedError


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
