from __future__ import annotations

import chromadb
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore

from .paths import NOTES_DIR


COLLECTION_NAME = "brain"


def _store() -> ChromaVectorStore:
    db = chromadb.Client()
    collection = db.get_or_create_collection(COLLECTION_NAME)
    return ChromaVectorStore(chroma_collection=collection)


def build_index() -> None:
    docs = SimpleDirectoryReader(str(NOTES_DIR)).load_data()
    store = _store()
    VectorStoreIndex.from_documents(docs, vector_store=store)
    print("Index pronto")


def search_index(query: str) -> None:
    store = _store()
    index = VectorStoreIndex.from_vector_store(store)
    print(index.as_query_engine().query(query))
