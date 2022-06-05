import os
import glob
import logging

from haystack.document_stores import ElasticsearchDocumentStore

document_store = ElasticsearchDocumentStore(
        host="localhost", username="", password="", index="document", similarity="cosine"
    )

doc_count = document_store.get_document_count()
print(doc_count)