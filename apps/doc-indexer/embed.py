import os
import json
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

class LocalEmbedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Batch embed text chunks"""
        return self.model.encode(texts, convert_to_tensor=False).tolist()
    
    def embed_query(self, text: str) -> List[float]:
        """Embed single query"""
        return self.model.encode(text, convert_to_tensor=False).tolist()

class DocIndexer:
    def __init__(self, data_dir: str = "/home/unimate/unimate/data"):
        self.embedder = LocalEmbedder()
        self.data_dir = data_dir
        self.metadata_store = {}
        
        # Initialize ChromaDB
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chroma_client = chromadb.PersistentClient(path="/home/unimate/chroma_db")
        #self.collection = self.chroma_client.get_or_create_collection(
        #   name="document_chunks",
        #    metadata={"hnsw:space": "cosine"}
        #)


  

        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="doc_chunks",
            metadata={"hnsw:space": "cosine"}
        )
        
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def store_in_chromadb(self, doc_id: str, chunks: List[Dict], embeddings: List[List[float]]) -> Dict:
        """
        Store chunks and embeddings in ChromaDB
        """
        try:
            # Prepare data for ChromaDB
            ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
            documents = [chunk["chunk_text"] for chunk in chunks]
        
            # PROPER METADATA CLEANING - NO None VALUES
            metadatas = []
            for i, chunk in enumerate(chunks):
                # Get values with proper None handling
                page = chunk.get("page_number")
                heading = chunk.get("heading")
            
                # Ensure no None values
                metadata = {
                    "doc_id": doc_id,
                    "page": page if page is not None else 0,
                    "heading": heading if heading is not None else "",
                    "chunk_index": i
                }
                metadatas.append(metadata)

            # Add to ChromaDB collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
        
            return {
                "status": "success",
                "stored_count": len(chunks),
                "collection_size": self.collection.count()
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def process_file(self, filename: str) -> Dict:
        """Process a single JSON file from the data directory"""
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            with open(filepath, 'r') as f:
                chunks = json.load(f)
                
            if not isinstance(chunks, list):
                raise ValueError("Invalid format: Expected list of chunks")
                
            return self.process_and_store_chunks(filename, chunks)
            
        except Exception as e:
            return {
                "status": "error",
                "filename": filename,
                "error": str(e)
            }

    def process_and_store_chunks(self, doc_id: str, chunks: List[Dict]) -> Dict:
        """Process chunks, generate embeddings, and store in ChromaDB"""
        try:
            # Extract texts for embedding
            texts = [chunk["chunk_text"] for chunk in chunks]
            
            # Generate embeddings
            embeddings = self.embedder.embed_documents(texts)
            
            # Store in ChromaDB
            chroma_result = self.store_in_chromadb(doc_id, chunks, embeddings)
            
            if chroma_result["status"] == "error":
                raise Exception(f"ChromaDB storage failed: {chroma_result['error']}")
            
            # Also save embeddings to JSON file for backup
            output_path = os.path.join(self.data_dir, f"{doc_id}_embeddings.json")
            with open(output_path, 'w') as f:
                json.dump({
                    "doc_id": doc_id,
                    "embeddings": embeddings,
                    "metadata": [{
                        "page": chunk.get("page_number"),
                        "heading": chunk.get("heading")
                    } for chunk in chunks]
                }, f, indent=2)
                
            return {
                "status": "success",
                "doc_id": doc_id,
                "embedding_file": output_path,
                "chroma_result": chroma_result,
                "chunk_count": len(chunks),
                "sample_embedding": embeddings[0][:3]  # First 3 dimensions
            }
            
        except Exception as e:
            return {
                "status": "error",
                "doc_id": doc_id,
                "error": str(e)
            }

    def query_chromadb(self, query_text: str, n_results: int = 3) -> Dict:
        """Query ChromaDB for similar chunks"""
        try:
            # Embed the query
            query_embedding = self.embedder.embed_query(query_text)
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            return {
                "status": "success",
                "query": query_text,
                "results": results
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

if __name__ == "__main__":
    # Initialize with your data directory
    indexer = DocIndexer()
    
    # Process all JSON files in the data directory
    for filename in os.listdir(indexer.data_dir):
        if filename.endswith(".json") and not filename.endswith("_embeddings.json"):
            print(f"\n📄 Processing {filename}...")
            result = indexer.process_file(filename)
            print(json.dumps(result, indent=2))
    
    # Example query after processing
    print(f"\n🔍 Testing ChromaDB query...")
    query_result = indexer.query_chromadb("shipping requirements", n_results=2)
    print(json.dumps(query_result, indent=2))
