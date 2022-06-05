import os
import glob
import logging

from haystack.document_stores import ElasticsearchDocumentStore

from scratchpad.preprocessing.pre_processing import preprocess_text
from scratchpad.database.write_and_update_store import write_docs_and_update_embed
from scratchpad.retrievers import get_nn_retriever


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
RETRIEVER = "sentence-transformers/all-mpnet-base-v2"
PDF_LOC = "/home/dexter89_kp/Desktop/Deep_Learning_Papers"


def load_models():
    document_store = ElasticsearchDocumentStore(
        host="localhost", username="", password="", index="document", similarity="cosine"
    )
    st_retriever = get_nn_retriever(document_store, RETRIEVER)
    return document_store, st_retriever


def load_pdf_bulk(pdf_locations, document_store, st_retriever):
    pdf_proc_docs = preprocess_text(pdf_locations)
    logger.debug("Length of documents being inserted: {}".format(len(pdf_proc_docs)))
    write_docs_and_update_embed(document_store, pdf_proc_docs, st_retriever)


if __name__ == "__main__":
    doc_store, retriever = load_models()
    pdf_file_paths = glob.glob(os.path.join(PDF_LOC, "*"))
    print(pdf_file_paths)
    load_pdf_bulk(pdf_file_paths, doc_store, retriever)
