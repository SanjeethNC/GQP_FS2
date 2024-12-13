Step 0, Prerequisites-
Packages installed:
pip install chromadb==0.4.22
pip show chromadb (confirm version == 0.4.22)
pip install openpyxl
pip install streamlit
pip install "openai>=1.54.0,<2.0.0" (uses newer version matching new code)
pip install langchain-openai (if don't have this module)
pip install --upgrade langchain-openai (uses newer version matching new code)
pip install flask
pip install langchain_community
pip install watchdog
 
Optional (not sure if this made a difference):
pip install urllib3==1.26.15
 
Step 1, Add API key in secret
Remove filler text in chroma_retrieval.py, setup_chromadb.py and app.py
 
Step 2, Reference correct file name in code. Either way names should match.
Use df = pd.read_excel('df_with_metadata.xlsx')
 
vs.
df = pd.read_excel('df_with_metadata_2.xlsx')
 
In setup_chromadb.py
 
Step 3, Use different defined clients for Chroma DB and Open AI so no confusion.
 
Added client for Open AI
# Access the API key
client_oai = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
 
Reference as (use dot notation):
response = client_oai.embeddings.create(input=[text], model=model)
              embeddings.append(response.data[0].embedding)
 
And subsequently…
client_oai.RateLimitError and client_oai.InvalidRequestError
 
Keep for Chroma DB
client = chromadb.PersistentClient(path=chroma_db_path)
 
In both setup_chromadb.py and chroma_retrieval.py
 
Step 4, Update for API Using curl:
curl --location 'http://127.0.0.1:5000/api/sds?supplier=Jubilant%20Ingrevia%20Limited&product_name=4-Aminopyridine&query=hazard%2Cpf'
 
(updated parameter to be query= only vs. query_parameters=)
 
Step 5, running Streamlit:
The command to run the streamlit app is "streamlit run streamlit_api.py". Must have "logo.jpg" in the same folder as code for FS logo (try reloading the browser page that pops up if image isn't shown initially). Renamed the file for simplicity.
 
Test parameters (real data):
product_name=4-Aminopyridine
 
supplier=Jubilant Ingrevia Limited
 
query=hazard,pf