'''
Server code. Support following endpoints

1. Parse website and add to db
2. Parse multimedia and add to db
3. Parse document/list of documents and ad to db
4. Neural Semantic Search
5. Click through data from users
'''

from fastapi import FastAPI
from haystack.document_stores import ElasticsearchDocumentStore

from preprocessing.pre_processing import preprocess_readwise, preprocess_text, preprocess_add_websites, preprocess_add_videos
from database.write_and_update_store import write_docs_and_update_embed
from retrievers import get_es_retriever, get_nn_retriever


document_store = ElasticsearchDocumentStore(
    host="localhost", username="", password="", index="document", similarity="cosine"
)
st_retriever = get_nn_retriever(document_store, RETRIEVER)

app = FastAPI()

@app.get("/parse/url/")
def parse_website(url: str):
    url_processed_data = preprocess_add_websites([url])
    write_docs_and_update_embed(document_store, url_processed_data, st_retriever)


@app.get("/parse/document")
def parse_documents(docs: str):
    docs_processed_data = preprocess_text([docs])
    write_docs_and_update_embed(document_store, docs_processed_data, st_retriever)


@app.get("/parse/youtube")
def parse_youtube(url: str):
    yt_processed_data = preprocess_add_videos([url])
    write_docs_and_update_embed(document_store, yt_processed_data, st_retriever)


@app.get("/search")
def search(query: str):
    raise NotImplementedError


@app.get("/user_click_search")
def click_search_result(result: str):
    raise NotImplementedError
