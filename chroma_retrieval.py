# chroma_retrieval.py

import openai
import chromadb
import pandas as pd
import logging
import time

# Define your ChromaDB client and collection as a global variable
chroma_db_path = "Chroma_db_storage"
client = chromadb.PersistentClient(path=chroma_db_path)

# Attempt to get the collection, or create it if it doesn't exist
collection_name = "openai_sds_embeddings_metadata"
try:
    collection = client.get_collection(collection_name)
    print(f"Collection '{collection_name}' loaded successfully.")
except ValueError:  # Collection doesn't exist
    collection = client.create_collection(collection_name)
    print(f"Collection '{collection_name}' created successfully.")

# Section mapping for metadata
SECTION_MAPPING = {
    1: "Identification",
    2: "Hazards identification",
    3: "Composition/information on ingredients",
    4: "First aid measures",
    5: "Firefighting measures",
    6: "Accidental release measures",
    7: "Handling and storage",
    8: "Exposure controls/personal protection",
    9: "Physical and chemical properties",
    10: "Stability and reactivity",
    11: "Toxicological information",
    12: "Ecological information",
    13: "Disposal considerations",
    14: "Transport information",
    15: "Regulatory information",
    16: "Other information"
}

# Function to generate processed metadata for each row
def generate_processed_metadata(df):
    """Generates metadata for each row, with each section mapped to the correct structure."""
    print("Generating processed metadata for each row...")
    sections = list(SECTION_MAPPING.values())
    
    def process_row(row):
        processed_metadata = []
        for section_id, section_name in enumerate(sections, start=1):
            metadata_entry = {
                "page_content": row[section_name] if pd.notnull(row[section_name]) else "",
                "metadata": {
                    "File Name": row["File Name"],
                    "product_name": row["Product Name "],
                    "supplier": row["Supplier Name"],
                    "section_id": section_id
                }
            }
            processed_metadata.append(metadata_entry)
        return processed_metadata

    df['processed_metadata'] = df.apply(process_row, axis=1)
    print("Processed metadata generated successfully.")
    return df

# Setup logging configuration
logging.basicConfig(filename='chromadb_errors.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')



# Function to generate embeddings
def get_embeddings(texts, model="text-embedding-ada-002", retry_attempts=3):
    """Generates embeddings for a batch of texts using OpenAI API."""
    embeddings = []
    for text in texts:
        attempt = 0
        while attempt < retry_attempts:
            try:
                # Call the API for each text
                response = openai.Embedding.create(input=[text], model=model)
                embeddings.append(response['data'][0]['embedding'])
                break
            except openai.error.RateLimitError:
                print(f"Rate limit reached for text: {text}. Retrying...")
                time.sleep(5)  # Wait before retrying
                attempt += 1
            except openai.error.InvalidRequestError as e:
                print(f"Invalid input for text: {text}. Skipping. Error: {e}")
                embeddings.append(None)  # Append None for invalid input
                break
            except Exception as e:
                print(f"Unexpected error for text: {text}. Error: {e}")
                embeddings.append(None)
                break
        else:
            print(f"Failed to process text after {retry_attempts} attempts: {text}")
            embeddings.append(None)
    return embeddings



def store_sds_documents_to_chromadb(df, collection):
    """Stores each section of each document in ChromaDB with embeddings and metadata."""
    print("Storing SDS documents to ChromaDB...")
    successful_stores = 0
    failed_stores = 0

    for index, row in df.iterrows():
        for section in row.get('processed_metadata', []):
            try:
                page_content = section.get('page_content', '').strip()
                metadata = section.get('metadata', {})
                
                if not page_content or not metadata:
                    print(f"Missing content or metadata in section: {section}")
                    failed_stores += 1
                    continue

                # Generate embedding for the content
                embedding = get_embeddings([page_content])[0]
                
                if embedding:
                    collection.add(
                        embeddings=[embedding],
                        documents=[page_content],
                        ids=[f"{index}_{metadata.get('section_id', 'unknown')}"],
                        metadatas=[metadata]
                    )
                    successful_stores += 1
                else:
                    print(f"Failed to generate embedding for section: {section}")
                    failed_stores += 1
            except Exception as e:
                print(f"Unexpected error storing section: {section}. Error: {e}")
                failed_stores += 1

    print(f"Storage complete. Successes: {successful_stores}, Failures: {failed_stores}")

# NOTE: This is not being used in the API. We are using contextual compression included in the app.py code
# Multi-parameter retrieval function with similarity search 
def multi_retrieve_section(product_name, query_parameters=None, supplier=None, section_id=None):
    """Retrieves relevant sections based on product_name, optional supplier, section_id, and query_parameters."""
    print(f"Retrieving sections for product '{product_name}' with query parameters {query_parameters}...")
    # Step 1: Initial filter by product_name
    product_results = collection.get(where={"product_name": product_name})
    
    # Step 2: Further filter by supplier if provided
    if supplier:
        supplier_results = [
            {"document": doc, "metadata": meta}
            for doc, meta in zip(product_results['documents'], product_results['metadatas'])
            if meta.get("supplier") == supplier
        ]
    else:
        supplier_results = [
            {"document": doc, "metadata": meta}
            for doc, meta in zip(product_results['documents'], product_results['metadatas'])
        ]
    
    # Step 3: Further filter by section_id if provided
    if section_id:
        final_results = [
            {"document": result["document"], "metadata": result["metadata"]}
            for result in supplier_results
            if result["metadata"].get("section_id") == section_id
        ]
    else:
        final_results = supplier_results

    # Step 4: Perform similarity search for each query_parameter if provided
    if query_parameters:
        matched_results = []
        unmatched_in_section = False
        
        for query in query_parameters:
            query_embedding = get_embedding(query)
            
            if query_embedding:
                highest_similarity = -1
                best_match = None
                embeddings = [get_embedding(doc["document"]) for doc in final_results]
                
                # Find the document with the highest similarity score for the current query
                for idx, embedding in enumerate(embeddings):
                    similarity = sum([a * b for a, b in zip(query_embedding, embedding)])  # Dot product similarity
                    if similarity > highest_similarity:
                        highest_similarity = similarity
                        best_match = final_results[idx]
                
                if best_match:
                    matched_results.append(best_match)
                else:
                    unmatched_in_section = True  # Track if some queries didn't match in the section

        # Step 5: Handle case when section_id is specified and no matches found
        if section_id and unmatched_in_section:
            print("No matching results found in the specified section.")
            return {
                "error": "No matching results found in the specified section.",
                "suggestion": "Remove section_id to search across all sections for broader results."
            }
        
        # Return all matched results with highest similarity scores for each query
        if matched_results:
            print(f"Found {len(matched_results)} matching results with similarity search.")
            return [
                {
                    "product_name": result['metadata']['product_name'],
                    "supplier": result['metadata'].get('supplier', 'Not Provided'),
                    "section_id": result['metadata']['section_id'],
                    "query_parameter": query_parameters,
                    "page_content": result['document']
                }
                for result in matched_results
            ]
    
    # Step 6: If no query_parameters or similarity search fails, return the first filtered result
    if final_results:
        document = final_results[0]["document"]
        metadata = final_results[0]["metadata"]
        print("Returning the first available result after filtering.")
        return {
            "product_name": metadata['product_name'],
            "supplier": metadata.get('supplier', 'Not Provided'),
            "section_id": metadata['section_id'],
            "query_parameter": query_parameters,
            "page_content": document
        }
    
    print("No matching section found.")
    return None
