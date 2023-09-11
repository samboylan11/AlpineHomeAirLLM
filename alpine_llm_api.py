# Alpine Home Air LLM
# Created September 10th 2023

# Import Statements
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import requests
from bs4 import BeautifulSoup
import time

# Langchain & Pinecone imports for LLM extensions
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
import pinecone

# Instantiate API
app = FastAPI()

# Fetch required API Keys from environment variables
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
PINECONE_API_ENV = os.environ.get('PINECONE_API_ENV')

# Instantiate Embeddings Object from OpenAI
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# Instantiate ChatGPT LLM
llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)

# Initialize Pinecone
pinecone.init(
    api_key=PINECONE_API_KEY,  # find at app.pinecone.io
    environment=PINECONE_API_ENV  # next to API key in console
)


# Index name to create on pinecone (Can only create one index on free package)
index_name = "python-index"

# Create index if it doesn't exist
if index_name not in pinecone.list_indexes():
    pinecone.create_index("python-index", dimension=1536, metric="cosine")
    # wait a moment for the index to be fully initialized
    time.sleep(1)

# Connect to the index
index = pinecone.Index(index_name)

# Scrape from any URL and extract the Text.
# TODO: Preprocessing Techniques to clean the scraped webpage data.
def scrape_text_from_url(url):
    # Fetch HTML content from URL
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for successful status code
    except requests.RequestException as e:
        print(f"An error occurred while fetching data: {e}")
        return None

    # Parse HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract all text from page
    all_text = ''
    for text in soup.stripped_strings:
        all_text += text + ' '

    return all_text

# Class to store posted data.
class ChatInput(BaseModel):
    prompt: str
    web_url: str

# LLM Chat API Endpoint
@app.post("/chat/", response_class=PlainTextResponse)
async def chat(chat_input: ChatInput):
    
    # Re-init pinecoin, sometimes there is an issue where it doesnt fetch latest created index on pinecone, so re-initializing on call is the fix for now.
    pinecone.init(
    api_key=PINECONE_API_KEY,  # find at app.pinecone.io
    environment=PINECONE_API_ENV  # next to API key in console
    )
    
    # Load QA Chain for Chatbot
    chain = load_qa_chain(llm, chain_type="stuff")

    print("Received Request")
    
    # Input Data
    prompt = chat_input.prompt
    url = chat_input.web_url
    
    # Scrape webpage
    test = scrape_text_from_url(url)
    
    # Split text recursively to find best combinations of sentences.
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    
    # Split the text
    texts = text_splitter.split_text(test)

    # Total Documents
    print (f'You have {len(texts)} document(s) in your data')
    
    # Create Embedding
    docsearch = Pinecone.from_texts([t for t in texts], embeddings, index_name=index_name)
    
    # Perform similarity search to find matching documents in embedding
    docs = docsearch.similarity_search(prompt)

    # Query the documents and get the answer
    response = chain.run(input_documents=docs, question=prompt)

    # Return response
    return response
