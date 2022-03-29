import os
import glob
import logging
import tempfile
import json
from typing import Sequence

from haystack.nodes import Crawler


logger = logging.getLogger(__name__)


def scrape_website_to_dict(urls: Sequence[str]):
    crawler = Crawler(output_dir=tempfile.gettempdir())

    # fetch only the url, do not traverse its sources
    docs = crawler.crawl(urls=urls, crawler_depth=0)

    # read json and return dict format expected in later pre-processing steps
    url_docs = []
    for jsonf in docs:
        with open(jsonf, "r") as f:
            jsonf_data = json.load(f)
        url_docs.append(jsonf_data)

    return url_docs
