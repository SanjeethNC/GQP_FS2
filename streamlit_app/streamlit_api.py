import requests
import streamlit as st

# Add an image at the top
st.image(
    "logo.jpg",
    use_container_width=True,
)

# Streamlit App Configuration
st.title("SDS Retrieval App")

# Custom CSS to reduce subheader size
st.markdown(
    """
    <style>
    .custom-subheader {
        font-size: 1.02rem; /* Reduce font size */
        color: #333333;
    }
    </style>
    <div class="custom-subheader">
        Provide Product Name and Supplier in the sidebar, then enter your query below to retrieve SDS content.
    </div>
    """,
    unsafe_allow_html=True,
)

# Custom CSS to change sidebar color to #8CB451
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background-color: #8CB451; /* New green color */
        color: white;
    }
    [data-testid="stSidebar"] input {
        color: black; /* Adjust input text color */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# User Input Section
st.sidebar.header("Input Parameters")
product_name = st.sidebar.text_input("Product Name", value="ExampleProduct")
supplier = st.sidebar.text_input("Supplier", value="ExampleSupplier")
section_id = st.sidebar.text_input("Section ID (comma-separated)", value="")
query = st.text_input("Query", placeholder="Enter your search query")

# API Base URL
API_BASE_URL = "http://127.0.0.1:5000/api"

# Function to Query the API
def fetch_sds_data(product_name, supplier, section_id, query):
    try:
        # Prepare the API request
        params = {
            "product_name": product_name,
            "supplier": supplier,
            "section_id": section_id,
            "query": query,
        }
        response = requests.get(f"{API_BASE_URL}/sds", params=params)

        # Handle API response
        if response.status_code == 200:
            return response.json()["data"]["results"]
        else:
            st.error(f"Error: {response.json().get('message', 'Unknown error')}")
            return []
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return []

# Button to Trigger Search
if st.button("Search SDS Content"):
    if not product_name or not supplier or not query:
        st.warning("Please fill in all required fields: Product Name, Supplier, and Query.")
    else:
        st.info("Fetching data from the API...")
        results = fetch_sds_data(product_name, supplier, section_id, query)

        # Display Results
        if results:
            st.success(f"Found {len(results)} result(s):")
            for idx, result in enumerate(results, start=1):
                with st.expander(f"Result {idx}"):
                    st.write("**Content:**", result["content"])
                    st.json(result["metadata"])
        else:
            st.warning("No results found.")