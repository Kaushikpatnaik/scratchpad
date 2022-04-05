import pandas as pd
import pytest
import glob

from haystack.telemetry import disable_telemetry
from scratchpad.preprocessing.document_converter import (
    generate_docx_docs,
    generate_md_docs,
    generate_pdf_docs,
    generate_txt_docs,
    generate_readwise_docs,
)
from scratchpad.preprocessing.pre_processing import preprocess_text, preprocess_readwise

disable_telemetry()


@pytest.fixture
def test_file_list():
    return glob.glob("test/test_files/*")


@pytest.fixture
def test_readwise_file():
    return "test/test_files/readwise-data_test.csv"


def test_generate_docx_docs(test_file_list):
    expected_docx_docs = [
        "A DeFi crash course for normies_ Crypto markets since 2017.docx"
    ]
    gen_docs = generate_docx_docs(test_file_list)
    assert all(
        [
            True if x["meta"]["file_name"] in expected_docx_docs else False
            for x in gen_docs
        ]
    )
    assert len(gen_docs) == len(expected_docx_docs)


def test_generate_md_docs(test_file_list):
    expected_md_docs = ["activation function.md"]
    gen_docs = generate_md_docs(test_file_list)
    assert all(
        [
            True if x["meta"]["file_name"] in expected_md_docs else False
            for x in gen_docs
        ]
    )
    assert len(gen_docs) == len(expected_md_docs)


def test_generate_pdf_docs(test_file_list):
    expected_pdf_docs = ["CoAtNet: Marrying Convolution and Attention.pdf"]
    gen_docs = generate_pdf_docs(test_file_list)
    assert all(
        [
            True if x["meta"]["file_name"] in expected_pdf_docs else False
            for x in gen_docs
        ]
    )
    assert len(gen_docs) == len(expected_pdf_docs)


def test_generate_txt_docs(test_file_list):
    expected_txt_docs = ["sample3.txt"]
    gen_docs = generate_txt_docs(test_file_list)
    assert all(
        [
            True if x["meta"]["file_name"] in expected_txt_docs else False
            for x in gen_docs
        ]
    )
    assert len(gen_docs) == len(expected_txt_docs)


def test_generate_readwise_docs(test_readwise_file):
    expected_len = len(pd.read_csv(test_readwise_file))
    gen_docs = generate_readwise_docs(test_readwise_file)
    assert len(gen_docs) == expected_len


def test_preprocess_test(test_file_list):
    processed_docs = preprocess_text(test_file_list)
    processed_docs_filenames = list(
        set([x["meta"]["file_name"] for x in processed_docs])
    )
    expected_filenames = [
        "A DeFi crash course for normies_ Crypto markets since 2017.docx",
        "activation function.md",
        "CoAtNet: Marrying Convolution and Attention.pdf",
        "sample3.txt",
    ]
    assert len(processed_docs) > 1
    assert sorted(expected_filenames) == sorted(processed_docs_filenames)


def test_preprocess_readwise(test_readwise_file):
    processed_docs = preprocess_readwise(test_readwise_file)
    assert len(processed_docs) == 173
