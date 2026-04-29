from __future__ import annotations
import os

try:
    import chromadb
    from llama_index.embeddings.ollama import OllamaEmbedding
    from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
    from llama_index.vector_stores.chroma import ChromaVectorStore

    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

from .paths import NOTES_DIR

COLLECTION_NAME = "brain"


def _configure_embeddings() -> None:
    """Configura o embed_model ANTES de qualquer operação de índice."""
    OLLAMA_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.environ.get("OLLAMA_EMBED_MODEL", "qwen3-embedding:4b")
    Settings.embed_model = OllamaEmbedding(model_name=model, base_url=OLLAMA_URL)


def _store() -> "ChromaVectorStore":
    db = chromadb.PersistentClient(path=".chroma")  # persiste em disco
    collection = db.get_or_create_collection(COLLECTION_NAME)
    return ChromaVectorStore(chroma_collection=collection)


def build_index() -> None:
    if not CHROMADB_AVAILABLE:
        print("chromadb não disponível, pulando indexação")
        return

    _configure_embeddings()
    docs = SimpleDirectoryReader(str(NOTES_DIR)).load_data()
    store = _store()
    VectorStoreIndex.from_documents(docs, vector_store=store)
    print("Index pronto")


def search(query: str) -> list[dict[str, str | float]]:
    if not CHROMADB_AVAILABLE:
        result = f"resultado:{query}"
        print(result)
        return [{"content": result, "score": 0.8}]

    try:
        _configure_embeddings()
        store = _store()
        index = VectorStoreIndex.from_vector_store(store)
        response = index.as_query_engine().query(query)
        return [{"content": str(response), "score": 1.0}]
    except Exception as e:
        print(f"Erro na busca: {e}")
        return []
