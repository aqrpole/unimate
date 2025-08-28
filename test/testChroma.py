import chromadb
from chromadb.config import Settings

def check_chroma_db():
    try:
        # Initialize the ChromaDB client with the new API
        client = chromadb.PersistentClient(path="/home/unimate/chroma_db")

        # List all collections
        collections = client.list_collections()
        print("Available collections:")
        for collection in collections:
            print(f"- {collection.name}")
            
            # Get collection info
            col = client.get_collection(collection.name)
            count = col.count()
            print(f"  Documents in collection: {count}")
            
            # Get sample data if any exists
            if count > 0:
                results = col.get(include=["documents", "metadatas"], limit=min(5, count))
                print("  Sample documents:")
                for i, (doc, meta) in enumerate(zip(results['documents'], results['metadatas'])):
                    print(f"    {i+1}. {doc[:100]}... (Metadata: {meta})")
        
        print("\nTesting query...")
        # Test a query on the first collection if any exist
        if collections:
            collection = client.get_collection(collections[0].name)
            results = collection.query(
                query_texts=["shipping requirements"],
                n_results=3,
                include=["documents", "metadatas", "distances"]
            )
            print("Query results structure:", {k: type(v) for k, v in results.items()})
            if results['ids'] and len(results['ids']) > 0:
                print("Query returned", len(results['ids'][0]), "results")
                for i, (doc_id, doc_text, metadata) in enumerate(zip(results['ids'][0], results['documents'][0], results['metadatas'][0])):
                    print(f"  {i+1}. ID: {doc_id}")
                    print(f"     Document: {doc_text[:100]}...")
                    print(f"     Metadata: {metadata}")
        
        return True
        
    except Exception as e:
        print(f"Error accessing ChromaDB: {e}")
        return False

def test_chroma_connection():
    """Test basic ChromaDB functionality"""
    try:
        # Test with a temporary in-memory client first
        client = chromadb.Client()
        test_collection = client.create_collection("test_collection")
        
        # Add test data
        test_collection.add(
            documents=["This is a test document about shipping requirements"],
            metadatas=[{"source": "test", "page": 1}],
            ids=["test_doc_1"]
        )
        
        # Query test data
        results = test_collection.query(
            query_texts=["shipping"],
            n_results=1,
            include=["documents", "metadatas", "distances"]
        )
        
        print("Test connection successful!")
        print("Test collection count:", test_collection.count())
        print("Test query results:", results)
        
        # Clean up
        client.delete_collection("test_collection")
        return True
        
    except Exception as e:
        print(f"Test connection failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing ChromaDB connection...")
    test_success = test_chroma_connection()
    
    print("\n" + "="*50)
    print("Checking your ChromaDB instance...")
    check_success = check_chroma_db()
    
    print("\n" + "="*50)
    if test_success and check_success:
        print("✓ Both tests completed successfully")
    else:
        print("✗ Some tests failed - check your ChromaDB installation")
