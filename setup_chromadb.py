# setup_chromadb.py

import os
import pandas as pd
from chroma_retrieval import get_embedding, generate_processed_metadata, store_sds_documents_to_chromadb



# Set up OpenAI API key
os.environ['OPENAI_API_KEY'] = 'Enter_key_here'

# Load data from Excel file
print("Loading data from Excel file...")
df = pd.read_excel('df_with_metadata.xlsx')
print("Columns in the DataFrame:", df.columns)

print("Data loaded successfully.")

# Generate processed metadata
df = generate_processed_metadata(df)

# Store data in ChromaDB
store_sds_documents_to_chromadb(df)
print("ChromaDB setup complete.")
