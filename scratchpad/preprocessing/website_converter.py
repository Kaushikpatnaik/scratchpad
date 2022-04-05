import logging
import tempfile
import json
import hashlib
from typing import Sequence

from haystack.nodes import Crawler


logger = logging.getLogger(__name__)


def scrape_website_to_dict(urls: Sequence[str]):
    crawler = Crawler(output_dir=tempfile.gettempdir())

    # fetch only the url, do not traverse its sources
    docs = crawler.crawl(urls=urls, crawler_depth=0)

    # read json and return dict format expected in later pre-processing steps
    url_docs = []
    for jsonf, url in zip(docs, urls):
        hash_object = hashlib.md5(str(url).encode("utf-8"))
        hash_string = hash_object.hexdigest()
        with open(jsonf, "r") as f:
            jsonf_data = json.load(f)
        jsonf_data["meta"]["file_name"] = url
        jsonf_data["meta"]["src_ptr"] = hash_string
        url_docs.append(jsonf_data)

    return url_docs
