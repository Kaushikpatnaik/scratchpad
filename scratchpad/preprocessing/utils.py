import glob
import os
import logging
from typing import List, Optional, Any, Dict

from google.cloud import storage
from haystack.nodes.file_converter import BaseConverter


logger = logging.getLevelName(__name__)


def list_all_files_folder(path):
    return [x for x in glob.glob(path) if x.endswith(".docx")]


def upload_blob(bucket_name, source_file_name):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    destination_blob_name = os.path.basename(source_file_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    return destination_blob_name


def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # source_blob_name = "storage-object-name"
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)


class StrConverter(BaseConverter):
    def convert(
        self,
        text: str,
        meta: Optional[Dict[str, str]] = None,
        remove_numeric_tables: Optional[bool] = None,
        valid_languages: Optional[List[str]] = None,
        encoding: Optional[str] = "utf-8",
    ) -> List[Dict[str, Any]]:
        """
        Reads string and executes optional preprocessing steps.
        :param file_path: path of the file to convert
        :param meta: dictionary of meta data key-value pairs to append in the returned document.
        :param remove_numeric_tables: This option uses heuristics to remove numeric rows from the tables.
                                      The tabular structures in documents might be noise for the reader model if it
                                      does not have table parsing capability for finding answers. However, tables
                                      may also have long strings that could possible candidate for searching answers.
                                      The rows containing strings are thus retained in this option.
        :param valid_languages: validate languages from a list of languages specified in the ISO 639-1
                                (https://en.wikipedia.org/wiki/ISO_639-1) format.
                                This option can be used to add test for encoding errors. If the extracted text is
                                not one of the valid languages, then it might likely be encoding error resulting
                                in garbled text.
        :param encoding: Select the file encoding (default is `utf-8`)
        :return: Dict of format {"text": "The text from file", "meta": meta}}
        """
        if remove_numeric_tables is None:
            remove_numeric_tables = self.remove_numeric_tables
        if valid_languages is None:
            valid_languages = self.valid_languages

        cleaned_pages = []
        for page in text:
            lines = page.splitlines()
            cleaned_lines = []
            for line in lines:
                words = line.split()
                digits = [word for word in words if any(i.isdigit() for i in word)]

                # remove lines having > 40% of words as digits AND not ending with a period(.)
                if remove_numeric_tables:
                    if (
                        words
                        and len(digits) / len(words) > 0.4
                        and not line.strip().endswith(".")
                    ):
                        logger.debug(f"Removing line '{line}' from {text}")
                        continue

                cleaned_lines.append(line)

            page = "\n".join(cleaned_lines)
            cleaned_pages.append(page)

        if valid_languages:
            document_text = "".join(cleaned_pages)
            if not self.validate_language(document_text, valid_languages):
                logger.warning(
                    f"The language for {text} is not one of {valid_languages}. The file may not have "
                    f"been decoded in the correct text format."
                )

        text = "".join(cleaned_pages)
        document = {"content": text, "content_type": "text", "meta": meta}
        return document
