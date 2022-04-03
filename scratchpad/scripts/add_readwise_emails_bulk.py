import os
import glob
import logging

from preprocessing.pre_processing import preprocess_readwise, preprocess_text
from database.write_and_update_store import write_docs_and_update_embed, document_store
from retrievers import get_es_retriever, get_nn_retriever


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
RETRIEVER = "sentence-transformers/all-mpnet-base-v2"

DATA_LOC = "/home/dexter89_kp/Desktop/scratchpad/data"
READWISE_FILE_NAME = "readwise-data_02022022.csv"
EMAILS_LOC = "emails"

st_retriever = get_nn_retriever(document_store, RETRIEVER)

readwise_proc_docs = preprocess_readwise([os.path.join(DATA_LOC, READWISE_FILE_NAME)])
logger.debug("Length of documents being inserted: {}".format(len(readwise_proc_docs)))
write_docs_and_update_embed(document_store, readwise_proc_docs, st_retriever)

email_file_list = glob.glob(os.path.join(DATA_LOC, EMAILS_LOC, "*"))
email_proc_docs = preprocess_text(email_file_list)
write_docs_and_update_embed(document_store, email_proc_docs, st_retriever)
