import os
import pandas as pd
import chromadb
from openai import OpenAI
from chroma_retrieval import get_embeddings, generate_processed_metadata, store_sds_documents_to_chromadb

# Set up OpenAI API key
os.environ['OPENAI_API_KEY'] = "Your API Key"

# Access the API key
client_oai = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# Initialize ChromaDB client
print("Initializing ChromaDB client...")
chroma_db_path = "Chroma_db_storage"
client = chromadb.PersistentClient(path=chroma_db_path)

# Create or get collection
collection_name = "openai_sds_embeddings_metadata"
try:
    collection = client.get_collection(collection_name)
    print(f"Collection '{collection_name}' loaded successfully.")
except ValueError:  # Collection doesn't exist
    collection = client.create_collection(collection_name)
    print(f"Collection '{collection_name}' created successfully.")

# Load data from Excel file
print("Loading data from Excel file...")
df = pd.read_excel('df_with_metadata.xlsx')
print("Columns in the DataFrame:", df.columns)
print("Data loaded successfully.")

# Generate processed metadata
print("Generating processed metadata for each row...")
df = generate_processed_metadata(df)
print("Processed metadata generated successfully.")

# Store data in ChromaDB
print("Storing data in ChromaDB...")
store_sds_documents_to_chromadb(df, collection)
print("ChromaDB setup complete.")
