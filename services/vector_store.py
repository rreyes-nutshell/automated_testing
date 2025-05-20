import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer

# Use SentenceTransformers with all-MiniLM
model = SentenceTransformer("all-MiniLM-L6-v2")

chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="ollama_memory")

def embed_and_store(session_id, prompt, response):
    content = f"PROMPT:\n{prompt}\n\nRESPONSE:\n{response}"
    embedding = model.encode(content).tolist()
    collection.add(
        documents=[content],
        embeddings=[embedding],
        ids=[f"{session_id}-{len(collection.get()['ids'])}"],
        metadatas=[{"session_id": session_id}]
    )

def query_similar(session_id, new_prompt, top_k=3):
    embedding = model.encode(new_prompt).tolist()
    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k,
        where={"session_id": session_id}
    )
    return results["documents"][0] if results["documents"] else []