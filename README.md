
## Table of Contents
- [Project Structure](#project-structure)
- [Setup Guide](#setup-guide)
  - [Prerequisites](#prerequisites)
  - [Installation Steps](#installation-steps)
- [API Usage](#api-usage)
  - [Endpoint Details](#endpoint-details)
  - [Example Usage](#example-usage)

## Structure

- `Chunking.ipynb`: Jupyter Notebook to format and chunk data, preparing it for insertion into ChromaDB
- `setup_chromadb.py`: Python script to load, process, and store data in ChromaDB
- `chroma_retrieval.py`: Utility functions for generating embeddings, standardizing metadata, and retrieving data from ChromaDB
- `app.py`: Flask API server for querying SDS data from ChromaDB

## Setup Guide

### Prerequisites

- Python 3.7+
- Required Python libraries (install using pip)

```bash
pip install -r requirements.txt
```

### Installation Steps

#### Step 1: Prepare Chunked Data

Run the Jupyter Notebook `Chunking.ipynb` to process raw data into a standardized, chunked format:

1. Open `Chunking.ipynb`
2. Run all cells to process and output the formatted dataset
3. Save the output as a file for use in the next step

#### Step 2: Set Up ChromaDB with Chunked Data

Run the setup script to load the chunked data, generate embeddings, and store it in ChromaDB:

```bash
python setup_chromadb.py
```

This script:
- Loads the chunked data file
- Generates embeddings for each chunk
- Stores everything in ChromaDB with the necessary metadata

#### Step 3: Start the Flask API Server

Once data is stored in ChromaDB, start the Flask server:

```bash
python app.py
```

The API server will:
- Start at `http://127.0.0.1:5000`
- Display log messages in the console showing server status and data retrieval events

## API Usage

### Endpoint Details

#### GET `/api/sds`

**Parameters:**
- `product_name` (required): Name of the product to filter results
- `supplier` (optional): Name of the supplier to narrow down results
- `query_parameters` (optional): List of keywords to perform similarity-based search within the document
- `section_id` (optional): Specific section of SDS to retrieve

### Example Usage

#### Example Request

Using curl:
```bash
curl --location 'http://127.0.0.1:5000/api/sds?supplier=Jubilant%20Ingrevia%20Limited&product_name=4-Aminopyridine&query_parameters=hazard%2Cpf'
```

#### Example Response

```json
{
    "status": "success",
    "data": {
        "count": 1,
        "results": [
            {
                "product_name": "4-Aminopyridine",
                "supplier": "Jubilant Ingrevia Limited",
                "section_id": 5,
                "query_parameter": ["hazard", "pf"],
                "page_content": "Relevant SDS content for the specified search criteria."
            }
        ]
    }
}
```
