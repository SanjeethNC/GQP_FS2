import chromadb
import os

# Define the path to the ChromaDB storage
storage_path = "Chroma_db_storage"  # Make sure this matches your actual storage path

# Check if the storage path exists
if not os.path.exists(storage_path):
    print(f"Storage path '{storage_path}' does not exist.")
else:
    # Initialize ChromaDB Persistent Client with the specified path
    try:
        client = chromadb.PersistentClient(path=storage_path)
        print(f"Connected to ChromaDB storage at: {os.path.abspath(storage_path)}")

        # Define the collection name
        collection_name = "openai_sds_embeddings_metadata"

        # Try to load the collection
        try:
            collection = client.get_collection(collection_name)
            print(f"Collection '{collection_name}' loaded successfully.")
            
            # Print collection details
            print(f"Collection name: {collection_name}")
            print(f"Number of documents in collection: {collection.count()}")
        
        except chromadb.errors.InvalidCollectionException:
            print(f"Collection '{collection_name}' does not exist in the storage.")
        
    except Exception as e:
        print(f"Failed to connect to ChromaDB: {e}")
