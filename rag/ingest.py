import os
import chromadb
from chromadb.utils import embedding_functions

KB_DIR = os.path.join(os.path.dirname(__file__), 'knowledge_base')
DB_DIR = os.path.join(os.path.dirname(__file__), 'chroma_db')

def ingest_policies():
    # Initialize chroma client
    client = chromadb.PersistentClient(path=DB_DIR)
    
    # Use sentence-transformers
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    # Create or get collection
    collection = client.get_or_create_collection(
        name="policies",
        embedding_function=sentence_transformer_ef
    )
    
    documents = []
    ids = []
    metadatas = []
    
    # Simple chunking: since the files are small, treat each file as a single document 
    # or split by double newlines.
    for filename in os.listdir(KB_DIR):
        if not filename.endswith('.md'):
            continue
            
        file_path = os.path.join(KB_DIR, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Add the whole content as a chunk since they are short policies
        doc_id = f"{filename}_full"
        documents.append(content.strip())
        ids.append(doc_id)
        metadatas.append({"source": filename})
            
    if documents:
        collection.upsert(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
        print(f"Ingested {len(documents)} policy documents into ChromaDB.")

if __name__ == '__main__':
    ingest_policies()
