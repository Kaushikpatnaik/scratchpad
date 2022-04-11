from haystack.nodes import ElasticsearchRetriever
from haystack.nodes import EmbeddingRetriever


def get_es_retriever(doc_store):
    return ElasticsearchRetriever(doc_store)


def get_nn_retriever(doc_store, st_model):
    return EmbeddingRetriever(
        document_store=doc_store,
        embedding_model=st_model,
        model_format="sentence_transformers",
    )
