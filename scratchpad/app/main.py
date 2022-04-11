"""
Server code. Support following endpoints
1. Parse website and add to db
2. Parse multimedia and add to db
3. Parse document/list of documents and ad to db
4. Neural Semantic Search
5. Click through data from users
"""

from fastapi import FastAPI
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
)


DEFAULT_CONFIG = {
    "RANKER": "cross-encoder/ms-marco-MiniLM-L-6-v2",
    "ST_RETRIEVER": "sentence-transformers/all-mpnet-base-v2",
}


document_store = ElasticsearchDocumentStore(
    host="elasticsearch", username="", password="", index="document", similarity="cosine"
)
st_retriever = get_nn_retriever(document_store, DEFAULT_CONFIG.get("ST_RETRIEVER"))
bm25_ranker = bm25_ranker_search_pipeline(document_store, config=DEFAULT_CONFIG)
dense_ranker = dense_retriever_ranker_search_pipeline(
    document_store, config=DEFAULT_CONFIG
)


app = FastAPI()


@app.get("/parse/url/{url:path}")
def parse_website(url: str):
    url_processed_data = preprocess_add_websites([url])
    write_docs_and_update_embed(document_store, url_processed_data, st_retriever)


@app.get("/parse/document/{docs:path}")
def parse_documents(docs: str):
    docs_processed_data = preprocess_text([docs])
    write_docs_and_update_embed(document_store, docs_processed_data, st_retriever)


@app.get("/parse/youtube/{url:path}")
def parse_youtube(url: str):
    yt_processed_data = preprocess_add_videos([url])
    write_docs_and_update_embed(document_store, yt_processed_data, st_retriever)


@app.get("/search")
def search(query: str):
    bm25_results = pipeline_search(query, bm25_ranker)
    dense_results = pipeline_search(query, dense_ranker)
    return bm25_results + dense_results


@app.get("/user_click_search")
def click_search_result(result: str):
    raise NotImplementedError
