from __future__ import annotations
import os
import logging
from typing import Any

try:
    import chromadb
    from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
    from llama_index.vector_stores.chroma import ChromaVectorStore

    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

from .paths import NOTES_DIR, ROOT

logger = logging.getLogger(__name__)
COLLECTION_NAME = "brain"


def _configure_settings() -> None:
    """Configura embeddings/LLM antes de operações de índice e query.

    Importante: faz imports de integrações (Ollama) de forma lazy para que
    ambientes de teste possam injetar módulos fake em `sys.modules` sem
    misturar módulos reais e mockados.
    """
    OLLAMA_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

    from llama_index.embeddings.ollama import OllamaEmbedding

    embed_model_name = os.environ.get("OLLAMA_EMBED_MODEL", "mxbai-embed-large:latest")
    logger.debug(
        "[RAG] Configurando embeddings - URL: %s, Modelo: %s",
        OLLAMA_URL,
        embed_model_name,
    )
    Settings.embed_model = OllamaEmbedding(
        model_name=embed_model_name, base_url=OLLAMA_URL
    )

    # Busca semântica deste projeto usa recuperação vetorial (retriever), então
    # não configuramos LLM aqui para evitar exigir modelos grandes em memória.


def _store() -> "ChromaVectorStore":
    db_path = ROOT / ".chroma"
    if not db_path.exists():
        logger.info("[RAG] Criando diretório do banco de dados Chroma: %s", db_path)
        db_path.mkdir(parents=True, exist_ok=True)

    db = chromadb.PersistentClient(path=str(db_path))  # persiste em disco
    collection = db.get_or_create_collection(COLLECTION_NAME)
    return ChromaVectorStore(chroma_collection=collection)


def build_index() -> None:
    if not CHROMADB_AVAILABLE:
        logger.warning("[RAG] ChromaDB não disponível, pulando indexação")
        print("chromadb não disponível, pulando indexação")
        return

    _configure_settings()
    docs = SimpleDirectoryReader(str(NOTES_DIR)).load_data()
    store = _store()
    VectorStoreIndex.from_documents(docs, vector_store=store)
    print("Index pronto")


def search(query: str) -> list[dict[str, Any]]:
    if not CHROMADB_AVAILABLE:
        result = f"resultado:{query}"
        print(result)
        return [{"content": result, "score": 0.8}]

    try:
        _configure_settings()
        store = _store()
        index = VectorStoreIndex.from_vector_store(store)
        # Query via retriever avoids response synthesis with LLM, reducing RAM usage.
        retriever = index.as_retriever(similarity_top_k=5)
        nodes = retriever.retrieve(query)

        results: list[dict[str, Any]] = []
        for item in nodes:
            node = getattr(item, "node", None)
            if node is None:
                content = str(item)
                metadata: dict[str, Any] = {}
            else:
                if hasattr(node, "get_content"):
                    content = node.get_content()
                else:
                    content = str(node)
                metadata = getattr(node, "metadata", {}) or {}
            score = getattr(item, "score", 0.0) or 0.0
            source_path = (
                metadata.get("file_path")
                or metadata.get("file_name")
                or metadata.get("filename")
                or metadata.get("source")
            )
            results.append(
                {
                    "content": str(content),
                    "score": float(score),
                    "source": str(source_path) if source_path else None,
                }
            )

        return results
    except Exception as e:
        print(f"Erro na busca: {e}")
        return []
