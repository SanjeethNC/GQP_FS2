from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException, BadRequest
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_openai import OpenAI
from langchain_community.vectorstores import Chroma
from langchain.vectorstores import Chroma as LangChainChroma
from langchain_community.embeddings import OpenAIEmbeddings
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize Flask app
app = Flask(__name__)

# Step 1: Set up OpenAI API Key
os.environ["OPENAI_API_KEY"] = "Your API Key"

# Step 2: Define your ChromaDB client and collection
chroma_db_path = "Chroma_db_storage"
collection_name = "openai_sds_embeddings_metadata"
embedding_model = OpenAIEmbeddings()

vector_store = LangChainChroma(
    persist_directory=chroma_db_path,
    embedding_function=embedding_model,
    collection_name=collection_name
)

# Step 3: Set up ContextualCompressionRetriever
llm = OpenAI(temperature=0)  # Low-temperature LLM for accurate retrieval
#import chatopenAI for using GPT 4 and 4o and try hyperparameters

compressor = LLMChainExtractor.from_llm(llm)
retriever = vector_store.as_retriever(
    search_kwargs={"k": 10}  # Retrieve up to 10 results
)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor, base_retriever=retriever
)

# Standard error responses
def error_response(message, status_code=400):
    """Helper function to format error responses"""
    return jsonify({
        'status': 'error',
        'message': message,
        'status_code': status_code
    }), status_code

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'success',
        'message': 'API is up and running!'
    })

# SDS retrieval endpoint
@app.route('/api/sds', methods=['GET'])
def get_sds_content():
    try:
        # Extract query parameters
        product_name = request.args.get('product_name')
        supplier = request.args.get('supplier')
        section_id = request.args.get('section_id')  # Accept comma-separated input
        query = request.args.get('query')

        # Validate required parameters
        if not product_name or not query or not supplier:
            raise BadRequest("Missing required parameters: 'product_name' and/or 'query' and/or supplier")

        # Parse section_id into a list if provided
        section_ids = None
        if section_id:
            try:
                section_ids = [int(s.strip()) for s in section_id.split(",")]
            except ValueError:
                raise BadRequest("Invalid section_id format. Must be a comma-separated list of integers.")

        # Log parameters for debugging
        logging.info(f"Request parameters - product_name: {product_name}, supplier: {supplier}, section_id: {section_id}, query: {query}")

        # Construct filter for retrieval
        filter_criteria = {
            "$and": [{"product_name": {"$eq": product_name}}]
        }
        if supplier:
            filter_criteria["$and"].append({"supplier": {"$eq": supplier}})
        if section_ids:
            filter_criteria["$and"].append({"section_id": {"$in": section_ids}})

        # Log filter criteria
        logging.info(f"Filter criteria: {filter_criteria}")

        # Update retriever with filter
        retriever.search_kwargs["filter"] = filter_criteria

        # Retrieve compressed documents
        compressed_docs = compression_retriever.invoke(query)

        # Log retrieved documents
        logging.info(f"Retrieved documents: {compressed_docs}")

        # If no results are found
        if not compressed_docs:
            return error_response("No matching SDS content found.", 404)

        # Format results
        results = [
            {"content": doc.page_content, "metadata": doc.metadata}
            for doc in compressed_docs
        ]

        # Successful response
        return jsonify({
            'status': 'success',
            'data': {
                'count': len(results),
                'results': results
            }
        })

    except BadRequest as e:
        logging.error(f"BadRequest: {e}")
        return error_response(str(e), 400)

    except HTTPException as e:
        logging.error(f"HTTPException: {e}")
        return error_response(e.description, e.code)

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return error_response("An unexpected error occurred. Please try again later.", 500)

# Error handling for 404 Not Found
@app.errorhandler(404)
def not_found(error):
    return error_response("The requested resource was not found.", 404)

# Error handling for 405 Method Not Allowed
@app.errorhandler(405)
def method_not_allowed(error):
    return error_response("Method not allowed on this endpoint.", 405)

# Error handling for any uncaught exceptions
@app.errorhandler(Exception)
def handle_exception(e):
    # If the exception is an HTTPException, provide the status code
    if isinstance(e, HTTPException):
        return error_response(e.description, e.code)
    # For non-HTTP exceptions, log the error and return a 500 response
    logging.error(f"Unhandled Exception: {str(e)}")
    return error_response("Internal server error occurred. Please contact support if this issue persists.", 500)

# Start the Flask application
if __name__ == '__main__':
    app.run(debug=True)
