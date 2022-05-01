"""
Server code. Support following endpoints
1. Parse website and add to db
2. Parse multimedia and add to db
3. Parse document/list of documents and ad to db
4. Neural Semantic Search
5. Click through data from users
"""

import uvicorn
import shutil
from pathlib import Path
from os.path import exists

from fastapi import FastAPI, UploadFile, File
from haystack.document_stores import ElasticsearchDocumentStore

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


DEFAULT_CONFIG = {
    "RANKER": "cross-encoder/ms-marco-MiniLM-L-6-v2",
    "ST_RETRIEVER": "sentence-transformers/all-mpnet-base-v2",
}
FILE_UPLOAD_PATH = '/home/user/app/file-upload'
DEFAULT_PARAMS = {
    "ESRetriever": {"top_k": 3},
    "STRetriever": {"top_k": 3},
    "Ranker": {"top_k": 2}
}


document_store = ElasticsearchDocumentStore(
    host="elasticsearch", username="", password="", index="document", similarity="cosine"
)
st_retriever = get_nn_retriever(document_store, DEFAULT_CONFIG.get("ST_RETRIEVER"))
bm25_ranker = bm25_ranker_search_pipeline(document_store, config=DEFAULT_CONFIG)
dense_ranker = dense_retriever_ranker_search_pipeline(document_store, config=DEFAULT_CONFIG)
comb_ranker = combined_search_pipeline(document_store, config=DEFAULT_CONFIG)


app = FastAPI()


@app.get("/parse/url/{url:path}")
def parse_website(url: str):
    url_processed_data = preprocess_add_websites([url])
    write_docs_and_update_embed(document_store, url_processed_data, st_retriever)


@app.post("/parse/document")
def parse_documents(docs: UploadFile = File(...)):
    file_path = Path(FILE_UPLOAD_PATH) / f"{docs.filename}"
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(docs.file, buffer)
    docs_processed_data = preprocess_text([str(file_path)])
    write_docs_and_update_embed(document_store, docs_processed_data, st_retriever)


@app.get("/parse/youtube/{url:path}")
def parse_youtube(url: str):
    yt_processed_data = preprocess_add_videos([url])
    write_docs_and_update_embed(document_store, yt_processed_data, st_retriever)


@app.get("/comb_search")
def combined_search(query: str):
    comb_results = pipeline_search(query, comb_ranker, params=DEFAULT_PARAMS)
    return comb_results


@app.get("/bm25_search")
def bm25_search(query: str):
    mod_params = DEFAULT_PARAMS
    del mod_params["STRetriever"]
    bm25_results = pipeline_search(query, bm25_ranker, params=mod_params)
    return bm25_results


@app.get("/nn_search")
def nn_search(query: str):
    mod_params = DEFAULT_PARAMS
    del mod_params["ESRetriever"]
    dense_results = pipeline_search(query, dense_ranker, params=DEFAULT_PARAMS)
    return dense_results


@app.get("/user_click_search")
def click_search_result(result: str):
    raise NotImplementedError


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
