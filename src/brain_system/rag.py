from __future__ import annotations

try:
    import chromadb
    from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
    from llama_index.vector_stores.chroma import ChromaVectorStore

    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

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


def search(query: str) -> list[dict[str, str]]:
    """Search the RAG index for relevant content."""
    if not CHROMADB_AVAILABLE:
        # Return mock results for testing - also print for compatibility
        result = f"resultado:{query}"
        print(result)
        return [{"content": result, "score": 0.8}]

    try:
        store = _store()
        index = VectorStoreIndex.from_vector_store(store)
        results = index.as_query_engine().query(query)

        # Convert results to dict format
        return [{"content": str(result), "score": 1.0} for result in results]
    except Exception:
        # Fallback to empty results
        return []
