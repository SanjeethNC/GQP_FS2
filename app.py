from flask import Flask, request, jsonify
import chromadb
from typing import Optional

app = Flask(__name__)

# Initialize ChromaDB client
client = chromadb.PersistentClient(path="Chroma_db_storage")
collection = client.get_collection("sds_documents")

def retrieve_sds_content(collection, file_name=None, product_name=None, supplier=None, query_property=None):
    """
    Retrieve SDS content with various filters.
    [Previous function implementation remains the same]
    """
    # Build where clause based on single primary filter
    where_clause = None
    if file_name:
        where_clause = {"file_name": {"$eq": file_name}}
    elif product_name:
        where_clause = {"product_name": {"$eq": product_name}}
    elif supplier:
        where_clause = {"supplier": {"$eq": supplier}}
    elif query_property:
        where_clause = {"query_property": {"$eq": query_property}}

    # Get initial results
    results = collection.get(
        where=where_clause,
        include=['documents', 'metadatas']
    )

    # Apply additional filters in memory if needed
    filtered_results = []
    for i in range(len(results['ids'])):
        metadata = results['metadatas'][i]
        content = results['documents'][i]

        # Check if result matches all provided filters
        matches = True
        if file_name and metadata['file_name'] != file_name:
            matches = False
        if product_name and metadata['product_name'] != product_name:
            matches = False
        if supplier and metadata['supplier'] != supplier:
            matches = False
        if query_property and metadata['query_property'] != query_property:
            matches = False

        if matches:
            filtered_results.append({
                'content': content,
                'metadata': metadata
            })

    return filtered_results

@app.route('/api/sds', methods=['GET'])
def get_sds_content():
    """
    API endpoint to retrieve SDS content.
    Query parameters:
    - file_name: Name of the file
    - product_name: Name of the product
    - supplier: Name of manufacturer/supplier
    - query_property: Section type (e.g., "hazards", "first aid", etc.)
    """
    try:
        # Get query parameters
        file_name = request.args.get('file_name')
        product_name = request.args.get('product_name')
        supplier = request.args.get('supplier')
        query_property = request.args.get('query_property')

        # Validate that at least one parameter is provided
        if not any([file_name, product_name, supplier, query_property]):
            return jsonify({
                'error': 'At least one search parameter is required',
                'valid_parameters': ['file_name', 'product_name', 'supplier', 'query_property']
            }), 400

        # Retrieve results
        results = retrieve_sds_content(
            collection,
            file_name=file_name,
            product_name=product_name,
            supplier=supplier,
            query_property=query_property
        )

        # Return results
        return jsonify({
            'count': len(results),
            'results': results
        })

    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/sds/search', methods=['POST'])
def search_sds():
    """
    Advanced search endpoint that accepts JSON body with multiple search criteria
    """
    try:
        search_criteria = request.get_json()
        
        if not search_criteria:
            return jsonify({
                'error': 'Request body is required',
                'example': {
                    'file_name': 'optional',
                    'product_name': 'optional',
                    'supplier': 'optional',
                    'query_property': 'optional'
                }
            }), 400

        results = retrieve_sds_content(
            collection,
            file_name=search_criteria.get('file_name'),
            product_name=search_criteria.get('product_name'),
            supplier=search_criteria.get('supplier'),
            query_property=search_criteria.get('query_property')
        )

        return jsonify({
            'count': len(results),
            'results': results
        })

    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({'error': 'Method not allowed'}), 405

if __name__ == '__main__':
    app.run(debug=True)