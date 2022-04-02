def write_docs(db, dicts):
    db.write_documents(dicts)


def write_docs_and_update_embed(db, dicts, retriever):
    db.write_documents(dicts)
    print("Able to write documents")
    db.update_embeddings(retriever, update_existing_embeddings=False)


def update_all_embed(db, retriever):
    db.update_embeddings(retriever)
