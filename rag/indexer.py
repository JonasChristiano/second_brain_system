from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb


def build():
    docs = SimpleDirectoryReader("./vault/notes").load_data()
    db = chromadb.Client()
    col = db.get_or_create_collection("brain")

    store = ChromaVectorStore(chroma_collection=col)

    VectorStoreIndex.from_documents(docs, vector_store=store)
    print("Index pronto")


if __name__ == "__main__":
    build()
