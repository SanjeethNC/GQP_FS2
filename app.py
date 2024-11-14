# app.py

from flask import Flask, request, jsonify
from chroma_retrieval import multi_retrieve_section
from werkzeug.exceptions import HTTPException, BadRequest
import logging

app = Flask(__name__)

# Configure logging for debugging and error tracking
logging.basicConfig(level=logging.INFO)

# Standard error responses
def error_response(message, status_code=400):
    """Helper function to format error responses"""
    return jsonify({
        'status': 'error',
        'message': message,
        'status_code': status_code
    }), status_code

# Basic health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'success',
        'message': 'API is up and running!'
    })

# Main SDS retrieval endpoint
@app.route('/api/sds', methods=['GET'])
def get_sds_content():
    try:
        # Extract query parameters
        product_name = request.args.get('product_name')
        supplier = request.args.get('supplier')
        section_id = request.args.get('section_id', type=int)
        query_parameters = request.args.get('query_parameters')

        # Convert query_parameters to a list if provided
        if query_parameters:
            query_parameters = query_parameters.split(',')

        # Validate required parameters
        if not product_name:
            raise BadRequest("Missing required parameter: 'product_name'")

        # Retrieve results
        results = multi_retrieve_section(
            product_name=product_name,
            supplier=supplier,
            section_id=section_id,
            query_parameters=query_parameters
        )

        # If no results are found
        if not results:
            return error_response("No matching SDS content found.", 404)

        # Successful response
        return jsonify({
            'status': 'success',
            'data': {
                'count': len(results) if isinstance(results, list) else 1,
                'results': results
            }
        })

    except BadRequest as e:
        # Handle specific missing or bad request errors
        logging.error(f"BadRequest: {e}")
        return error_response(str(e), 400)

    except HTTPException as e:
        # Handle other HTTP-related exceptions
        logging.error(f"HTTPException: {e}")
        return error_response(e.description, e.code)

    except Exception as e:
        # Handle unexpected errors and log them
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
