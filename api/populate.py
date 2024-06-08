import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
from dotenv import load_dotenv
from tqdm import tqdm
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings

# Load environment variables from .env file
load_dotenv(dotenv_path=".env")

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# Initialize embedding function
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

def store_book_metadata(book_id, title, author, url):
    supabase.table('books').insert({
        'book_id': book_id,
        'title': title,
        'author': author,
        'url': url
    }).execute()

def store_book_embeddings(book_id, embeddings):
    supabase.table('book_embeddings').insert({
        'book_id': book_id,
        'embeddings': embeddings
    }).execute()

def scrape_book_metadata_and_generate_embeddings(book_id):
    metadata_url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.rdf"
    response = requests.get(metadata_url)
    if response.status_code != 200:
        print(f"Failed to retrieve metadata for book {book_id}")
        return
    
    soup = BeautifulSoup(response.content, 'lxml')

    title_tag = soup.find('dcterms:title')
    author_tag = soup.find('pgterms:name')
    
    if not title_tag or not author_tag:
        print(f"Skipping book {book_id} due to missing metadata")
        return

    title = title_tag.text
    author = author_tag.text
    book_url = f"https://www.gutenberg.org/cache/epub/{book_id}"

    text_url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt.utf8"
    text_response = requests.get(text_url)
    if text_response.status_code != 200:
        print(f"Failed to retrieve text for book {book_id}")
        return

    text_content = text_response.text

    # Generate embeddings for the text content
    embeddings = embedding_function.embed_text(text_content).tolist()

    store_book_metadata(book_id, title, author, book_url)
    store_book_embeddings(book_id, embeddings)
    print(f"Stored metadata and embeddings for book {book_id}")

if __name__ == "__main__":
    # Example usage
    for book_id in tqdm(range(1, 10)):  # Adjust range as needed
        scrape_book_metadata_and_generate_embeddings(book_id)
