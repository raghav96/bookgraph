import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up environment variables
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(supabase_url, supabase_key)

# Initialize embedding function
embedding_function = SentenceTransformer("all-MiniLM-L6-v2")

# Configure logging
logging.basicConfig(level=logging.INFO)

def store_book_metadata(book_id, title, author, url):
    response = supabase.table('books').insert({
        'id': book_id,
        'title': title,
        'author': author,
        'url': url
    }).execute()
    if response.status_code == 201:
        logging.info(f"Stored metadata for book {book_id}")
    else:
        logging.error(f"Failed to store metadata for book {book_id}: {response.text}")

def store_book_embeddings(book_id, embeddings):
    response = supabase.table('book_embeddings').insert({
        'book_id': book_id,
        'embeddings': embeddings
    }).execute()
    if response.status_code == 201:
        logging.info(f"Stored embeddings for book {book_id}")
    else:
        logging.error(f"Failed to store embeddings for book {book_id}: {response.text}")

def scrape_book_metadata_and_generate_embeddings(book_id):
    metadata_url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.rdf"
    response = requests.get(metadata_url)
    if response.status_code != 200:
        logging.error(f"Failed to retrieve metadata for book {book_id}")
        return
    
    soup = BeautifulSoup(response.content, 'lxml')

    title_tag = soup.find('dcterms:title')
    author_tag = soup.find('pgterms:name')
    
    if not title_tag or not author_tag:
        logging.warning(f"Skipping book {book_id} due to missing metadata")
        return

    title = title_tag.text
    author = author_tag.text
    book_url = f"https://www.gutenberg.org/cache/epub/{book_id}"

    text_url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt.utf8"
    text_response = requests.get(text_url)
    if text_response.status_code != 200:
        logging.error(f"Failed to retrieve text for book {book_id}")
        return

    text_content = text_response.text

    # Generate embeddings for the text content
    embeddings = embedding_function.encode(text_content).tolist()

    store_book_metadata(book_id, title, author, book_url)
    store_book_embeddings(book_id, embeddings)

# Example usage
for book_id in tqdm(range(673, 73756)):  # Adjust range as needed
    scrape_book_metadata_and_generate_embeddings(book_id)
