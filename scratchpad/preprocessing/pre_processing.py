"""
Top level file that runs converters, preprocesses them and adds them to 
database
"""

from typing import Sequence
from haystack.nodes import PreProcessor

from scratchpad.preprocessing.document_converter import (
    generate_readwise_docs,
    generate_docx_docs,
    generate_md_docs,
    generate_pdf_docs,
    generate_txt_docs,
)
from scratchpad.preprocessing.youtube_converter import generate_youtube_transcript_docs
from scratchpad.preprocessing.website_converter import scrape_website_to_dict


def preprocess_readwise(file: str, processor_args: dict = {}):
    """
    Given readwise export process the csv
    """

    processor = PreProcessor(
        clean_empty_lines=processor_args.get("clean_empty_lines", True),
        clean_whitespace=processor_args.get("clean_whitespace", True),
        clean_header_footer=processor_args.get("clean_header_footer", True),
        split_by=processor_args.get("split_by", "word"),
        split_length=processor_args.get("split_lenght", 200),
        split_respect_sentence_boundary=processor_args.get(
            "split_respect_sentence_boundary", True
        ),
        split_overlap=processor_args.get("split_overlap", 3),
    )

    readwise_docs = generate_readwise_docs(file)

    return processor.process(readwise_docs)


def preprocess_text(file_list: Sequence[str], processor_args: dict = {}):
    """
    Given list of documents to process, convert and preprocess them. Post processing,
    add them to the database
    """

    processor = PreProcessor(
        clean_empty_lines=processor_args.get("clean_empty_lines", True),
        clean_whitespace=processor_args.get("clean_whitespace", True),
        clean_header_footer=processor_args.get("clean_header_footer", True),
        split_by=processor_args.get("split_by", "word"),
        split_length=processor_args.get("split_lenght", 200),
        split_respect_sentence_boundary=processor_args.get(
            "split_respect_sentence_boundary", True
        ),
        split_overlap=processor_args.get("split_overlap", 3),
    )

    docx_docs = generate_docx_docs(file_list)
    pdf_docs = generate_pdf_docs(file_list)
    txt_docs = generate_txt_docs(file_list)
    md_docs = generate_md_docs(file_list)

    all_docs = docx_docs + pdf_docs + txt_docs + md_docs

    return processor.process(all_docs)


def preprocess_add_videos(url_list: Sequence[str], processor_args: dict = {}):

    processor = PreProcessor(
        clean_empty_lines=processor_args.get("clean_empty_lines", True),
        clean_whitespace=processor_args.get("clean_whitespace", True),
        clean_header_footer=processor_args.get("clean_header_footer", True),
        split_by=processor_args.get("split_by", "word"),
        split_length=processor_args.get("split_lenght", 200),
        split_respect_sentence_boundary=processor_args.get(
            "split_respect_sentence_boundary", True
        ),
        split_overlap=processor_args.get("split_overlap", 3),
    )

    youtube_docs = []
    for url in url_list:
        youtube_docs.append(generate_youtube_transcript_docs(url=url))

    return processor.process(youtube_docs)


def preprocess_add_websites(url_list: Sequence[str], processor_args: dict = {}):

    processor = PreProcessor(
        clean_empty_lines=processor_args.get("clean_empty_lines", True),
        clean_whitespace=processor_args.get("clean_whitespace", True),
        clean_header_footer=processor_args.get("clean_header_footer", True),
        split_by=processor_args.get("split_by", "word"),
        split_length=processor_args.get("split_lenght", 200),
        split_respect_sentence_boundary=processor_args.get(
            "split_respect_sentence_boundary", True
        ),
        split_overlap=processor_args.get("split_overlap", 3),
    )

    url_docs = scrape_website_to_dict(url_list)

    return processor.process(url_docs)
