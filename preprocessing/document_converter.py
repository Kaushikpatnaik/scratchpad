'''
Converters for text files, pdffiles, docx files, markdown files

Utilizes excellent Haystack repository and converters
'''

from haystack.nodes import TextConverter, PDFToTextConverter, DocxToTextConverter, MarkdownConverter, PreProcessor
from haystack.utils import convert_files_to_dicts, fetch_archive_from_http

text_converter = TextConverter(remove_numeric_tables=True)
pdf_converter = PDFToTextConverter(remove_numeric_tables=True)
docx_converter = DocxToTextConverter(remove_numeric_tables=True)
markdown_converter = MarkdownConverter(remove_numeric_tables=True)


