"""
Converters for text files, pdffiles, docx files, markdown files

Utilizes excellent Haystack repository and converters
"""

import os
import hashlib
from typing import List, Optional, Any, Dict
import logging

import numpy as np
import pandas as pd


from haystack.nodes import (
    TextConverter,
    PDFToTextConverter,
    DocxToTextConverter,
    MarkdownConverter,
)

from utils import list_all_files_folder, StrConverter


logger = logging.getLogger(__name__)
text_converter = TextConverter(remove_numeric_tables=True)
pdf_converter = PDFToTextConverter(remove_numeric_tables=True)
docx_converter = DocxToTextConverter(remove_numeric_tables=True)
markdown_converter = MarkdownConverter(remove_numeric_tables=True)
str_converter = StrConverter()


def _generate_docs(ext_filepaths, converter):
    if len(ext_filepaths) == 0:
        return []
    docs = []
    for filepath in ext_filepaths:
        filename = filepath.split("/")[-1]
        hash_object = hashlib.md5(str(filename).encode("utf-8"))
        hash_string = hash_object.hexdigest()
        doc = converter.convert(
            file_path=filepath, meta={"src_ptr": hash_string, "file_name": filename}
        )[0]
        docs.append(doc)

    return docs


def generate_docx_docs(file_paths):
    docs_filepaths = [x for x in file_paths if x.endswith(".docx")]
    return _generate_docs(docs_filepaths, docx_converter)


def generate_pdf_docs(file_paths):
    pdf_filepaths = [x for x in file_paths if x.endswith(".pdf")]
    return _generate_docs(pdf_filepaths, pdf_converter)


def generate_txt_docs(file_paths):
    txt_filepaths = [x for x in file_paths if x.endswith(".txt")]
    return _generate_docs(txt_filepaths, text_converter)


def generate_md_docs(file_paths):
    md_filepaths = [x for x in file_paths if x.endswith(".md")]
    return _generate_docs(md_filepaths, markdown_converter)


def generate_readwise_docs(readwise_file_path):
    data = pd.read_csv(readwise_file_path)

    data = data.drop(
        [
            "Amazon Book ID",
            "Note",
            "Color",
            "Tags",
            "Location Type",
            "Location",
            "Highlighted at",
        ],
        axis=1,
    )

    data.Highlight = data.Highlight.str.replace("\n", "")
    data.Highlight = data.Highlight.str.replace(r"\[|\]", "")

    data["doc_hash"] = data["Highlight"].apply(
        lambda x: hashlib.md5(str(x).encode("utf-8")).hexdigest()
    )
    data["index"] = data.index
    data = data.replace(np.nan, "", regex=True)
    data = data[["Highlight", "Book Title", "Book Author", "doc_hash", "index"]]
    data.columns = ["raw_string", "title", "author", "doc_hash", "index", "metadata"]

    readwise_docs = []
    for idx, row in data.iterrows():
        row_dict = str_converter.convert(
            row.raw_string,
            meta={"src_path": row.doc_hash, "title": row.title, "author": row.author},
        )
        readwise_docs.append(row_dict)

    return readwise_docs
