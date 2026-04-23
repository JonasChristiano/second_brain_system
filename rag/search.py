import sys
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb


def search(q):
    db = chromadb.Client()
    col = db.get_or_create_collection("brain")
    store = ChromaVectorStore(chroma_collection=col)

    index = VectorStoreIndex.from_vector_store(store)
    print(index.as_query_engine().query(q))


if __name__ == "__main__":
    search(sys.argv[1])
