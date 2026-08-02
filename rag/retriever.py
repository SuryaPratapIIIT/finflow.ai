import os
import chromadb
from chromadb.utils import embedding_functions

DB_DIR = os.path.join(os.path.dirname(__file__), 'chroma_db')

_client = None
_collection = None

def get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=DB_DIR)
        sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        _collection = _client.get_collection(
            name="policies",
            embedding_function=sentence_transformer_ef
        )
    return _collection

def retrieve(query: str, k: int = 3) -> list[str]:
    """
    Retrieves the top-k relevant policy chunks for a given query.
    """
    collection = get_collection()
    results = collection.query(
        query_texts=[query],
        n_results=k
    )
    
    if results and results['documents'] and len(results['documents']) > 0:
        return results['documents'][0]
    return []

if __name__ == '__main__':
    # Test the retriever
    test_query = "what happens if a customer is 45 days late"
    print(f"Query: '{test_query}'\n")
    docs = retrieve(test_query)
    for i, doc in enumerate(docs, 1):
        print(f"--- Result {i} ---")
        print(doc)
        print()
