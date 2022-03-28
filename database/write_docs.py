

def write_docs(db, dicts):
    db.write_documents(dicts)

def write_and_update_embed(db, dicts, retriever):
    db.write_documents(dicts)
    db.update_embeddings(retriever)