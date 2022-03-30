from haystack.document_stores import ElasticsearchDocumentStore

document_store = ElasticsearchDocumentStore(
    host="localhost", username="", password="", index="document"
)


def write_docs(db, dicts):
    db.write_documents(dicts)


def write_docs_and_update_embed(db, dicts, retriever):
    db.write_documents(dicts)
    db.update_embeddings(retriever, update_existing_embeddings=False)


def update_all_embed(db, retriever):
    db.update_embeddings(retriever)
