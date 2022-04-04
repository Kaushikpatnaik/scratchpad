import pytest

from scratchpad.preprocessing.document_converter import generate_docx_docs, generate_md_docs, generate_pdf_docs, generate_txt_docs, generate_readwise_docs

def test_generate_docx_docs(file_list, expected_docs_docs):
    gen_docs = generate_docx_docs(file_list)
    assert all([True for x in expected_docs_docs if x in gen_docs else False])
    assert len(gen_docs) == len(expected_docs_docs)


def test_generate_md_docs(file_list, expected_md_docs):
    gen_docs = generate_md_docs(file_list)
    assert all([True for x in expected_md_docs if x in gen_docs else False])
    assert len(gen_docs) == len(expected_md_docs)


def test_generate_pdf_docs(file_list, expected_pdf_docs):
    gen_docs = generate_pdf_docs(file_list)
    assert all([True for x in expected_pdf_docs if x in gen_docs else False])
    assert len(gen_docs) == len(expected_pdf_docs)


def test_generate_docx_docs(file_list, expected_txt_docs):
    gen_docs = generate_txt_docs(file_list)
    assert all([True for x in expected_txt_docs if x in gen_docs else False])
    assert len(gen_docs) == len(expected_txt_docs)
