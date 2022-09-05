import argparse
import os
import glob
import logging

from haystack.document_stores import ElasticsearchDocumentStore

from scratchpad.preprocessing.pre_processing import preprocess_readwise, preprocess_text, preprocess_add_websites
from scratchpad.database.write_and_update_store import write_docs_and_update_embed
from scratchpad.retrievers import get_nn_retriever


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
RETRIEVER = "sentence-transformers/all-mpnet-base-v2"

DATA_LOC = "/home/dexter89_kp/Desktop/scratchpad/data"
READWISE_FILE_NAME = "readwise-data_09_02_2022.csv"
EMAILS_LOC = "emails"


def load_models():
    document_store = ElasticsearchDocumentStore(
        host="localhost", username="", password="", index="document", similarity="cosine"
    )
    st_retriever = get_nn_retriever(document_store, RETRIEVER)
    return document_store, st_retriever


def load_readwise_bulk(document_store, st_retriever):
    readwise_proc_docs = preprocess_readwise(os.path.join(DATA_LOC, READWISE_FILE_NAME))
    logger.debug("Length of documents being inserted: {}".format(len(readwise_proc_docs)))
    write_docs_and_update_embed(document_store, readwise_proc_docs, st_retriever)


def load_pocker_urls(document_store, st_retriever, urls):
    url_proc_docs = preprocess_add_websites(urls)
    logger.debug("Length of documents being inserted: {}".format(len(url_proc_docs)))
    write_docs_and_update_embed(document_store, url_proc_docs, st_retriever)


if __name__ == "__main__":
    document_store, st_retriever = load_models()

    parser = argparse.ArgumentParser()
    parser.add_argument('--readwise', action='store_true')
    parser.add_argument('--pocket', action='store_true')

    args = parser.parse_args()

    if args.readwise:

        load_readwise_bulk(document_store, st_retriever)

    if args.pocket:

        from bs4 import BeautifulSoup
        f = open(os.path.join(DATA_LOC, "pocket_urls.html"))
        parsed_html = BeautifulSoup(f, 'html.parser')
        urls = []
        for idx, el in enumerate(parsed_html.find_all(href=True)):
            temp_url = el['href'].split('utm')[0][:-1]
            if 'medium' not in temp_url:
                if len(temp_url) < 150:
                    urls.append(temp_url)
        
        
        load_pocker_urls(document_store, st_retriever, urls[730:])