import os
import pandas as pd
import uuid
from supabase import create_client, Client
from dotenv import load_dotenv
from tqdm import tqdm
from langchain.vectorstores import SupabaseVectorStore
from langchain_core.documents import Document

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
client: Client = create_client(supabase_url, supabase_key)

# Load the CSV file
csv_path = '../data/pg_catalog.csv'
csv_data = pd.read_csv(csv_path)

# Initialize vector store
vector_store = SupabaseVectorStore(client, table_name="documents")

def fetch_book_data(book_id):
    book_response = client.from_('books').select('*').eq('id', book_id).single().execute()
    embedding_response = client.from_('book_embeddings').select('*').eq('book_id', book_id).single().execute()
    if book_response.error or embedding_response.error:
        print(f"Error fetching data for book_id {book_id}")
        return None, None
    return book_response.data, embedding_response.data

def create_content(book_data, csv_row):
    title = book_data.get('title', '')
    author = book_data.get('author', '')
    subjects = csv_row.get('subjects', '')
    bookshelves = csv_row.get('bookshelves', '')
    return f"{title}\n{author}\n{subjects}\n{bookshelves}"

def create_metadata(book_id, book_data):
    return {
        'book_id': book_id,
        'title': book_data.get('title', ''),
        'author': book_data.get('author', ''),
        'url': book_data.get('url', '')
    }

def populate_documents():
    for _, row in tqdm(csv_data.iterrows(), total=csv_data.shape[0]):
        book_id = str(row['book_id'])
        book_data, embedding_data = fetch_book_data(book_id)
        if book_data and embedding_data:
            content = create_content(book_data, row)
            metadata = create_metadata(book_id, book_data)
            embedding = embedding_data['embeddings']

            document = Document(
                page_content=content,
                metadata=metadata,
                embedding=embedding
            )

            try:
                vector_store.add_documents([document])
                print(f"Inserted document for book_id {book_id}")
            except Exception as e:
                print(f"Error inserting document for book_id {book_id}: {e}")

if __name__ == "__main__":
    populate_documents()
