'''
Converters for text files, pdffiles, docx files, markdown files

Utilizes excellent Haystack repository and converters
'''

import os
import hashlib
from typing import List, Optional, Any, Dict
import logging

import numpy as np
import pandas as pd


from haystack.nodes import TextConverter, PDFToTextConverter, DocxToTextConverter, MarkdownConverter, PreProcessor

from utils import list_all_files_folder, ReadwiseConverter


logger = logging.getLogger(__name__)
text_converter = TextConverter(remove_numeric_tables=True)
pdf_converter = PDFToTextConverter(remove_numeric_tables=True)
docx_converter = DocxToTextConverter(remove_numeric_tables=True)
markdown_converter = MarkdownConverter(remove_numeric_tables=True)


str_converter = ReadwiseConverter()


def generate_email_docs(email_dataset_path):
    docs_filepaths = list_all_files_folder(os.path.join(email_dataset_path, '*.docx'))

    docx_docs = []
    for docx_file in docs_filepaths:
        hash_object = hashlib.md5(str(docx_file).encode('utf-8'))
        hash_string = hash_object.hexdigest()
        doc_docx = docx_converter.convert(file_path = docx_file, meta = {"src_ptr": hash_string})[0]
        docx_docs.append(doc_docx)


def generate_readwise_docs(readwise_file_path):
    data = pd.read_csv(readwise_file_path)

    data = data.drop(['Amazon Book ID', 'Note', 'Color', 'Tags', 'Location Type', 'Location', 'Highlighted at'], axis=1)

    data.Highlight = data.Highlight.str.replace('\n', '')
    data.Highlight = data.Highlight.str.replace(r'\[|\]', '')

    data['doc_hash'] = data['Highlight'].apply(lambda x: hashlib.md5(str(x).encode('utf-8')).hexdigest())
    data['index'] = data.index
    data = data.replace(np.nan,'', regex=True)
    data = data[['Highlight', 'Book Title', 'Book Author', 'doc_hash', 'index']]
    data.columns = ['raw_string', 'title', 'author', 'doc_hash', 'index', 'metadata']

    readwise_docs = []
    for idx, row in data.iterrows():
        row_dict = str_converter.convert(row.raw_string, meta = {'src_path': row.doc_hash, 'title': row.title, 'author': row.author})
        readwise_docs.append(row_dict)
    
    return readwise_docs











