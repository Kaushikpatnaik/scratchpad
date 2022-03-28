'''
Top level file that runs converters, preprocesses them and adds them to 
database
'''

from haystack.nodes import PreProcessor

from document_converter import generate_email_docs, generate_readwise_docs
from youtube_converter import generate_youtube_transcript_docs
from website_converter import scrape_website_to_dict


def preprocess_add_documents(file_list: list):
    '''
    Given list of documents to process, convert and preprocess them. Post processing,
    add them to the database
    '''

    processor = PreProcessor(
    clean_empty_lines=True,
    clean_whitespace=True,
    clean_header_footer=True,
    split_by="word",
    split_length=200,
    split_respect_sentence_boundary=True,
    split_overlap=3
    )

    email_docs = generate_email_docs(file_list)
    readwise_docs = generate_readwise_docs(file_list)
    pdf_docs = generate_pdf_docs(file_list)

    all_docs = email_docs + readwise_docs + pdf_docs

    return processor.process(all_docs)


def preprocess_add_videos(url_list: list):

    processor = PreProcessor(
    clean_empty_lines=True,
    clean_whitespace=True,
    clean_header_footer=True,
    split_by="word",
    split_length=200,
    split_respect_sentence_boundary=True,
    split_overlap=3
    )

    youtube_docs = []
    for url in url_list:
        youtube_docs.append(generate_youtube_transcript_docs(url=url))
    
    return youtube_docs


def preprocess_add_websites(url_list: list):

    processor = PreProcessor(
    clean_empty_lines=True,
    clean_whitespace=True,
    clean_header_footer=True,
    split_by="word",
    split_length=200,
    split_respect_sentence_boundary=True,
    split_overlap=3
    )

    url_docs = []
    for url in url_list:
        url_docs += scrape_website_to_dict(url)

    return url_docs