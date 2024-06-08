import os
import pandas as pd
import uuid
from supabase import create_client, Client
from dotenv import load_dotenv
from tqdm import tqdm
from langchain.vectorstores import SupabaseVectorStore
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

embedding_function = SentenceTransformer("all-MiniLM-L6-v2")
# Load the CSV file
csv_path = 'mnt/data/pg_catalog.csv'
csv_data = pd.read_csv(csv_path)



def fetch_book_data(book_id):
    try:
        book_response = supabase.table('books').select('*').eq('book_id', book_id).single().execute()
        embedding_response = supabase.table('book_embeddings').select('*').eq('book_id', book_id).single().execute()
        
        return book_response.data, embedding_response.data

    except Exception as e:
        print(f"Exception occurred while fetching data for book_id {book_id}: {e}")
        return None, None


def create_metadata(book_id, book_data, csv_row):
    return {
        'book_id': book_id,
        'title': book_data.get('title', ''),
        'author': book_data.get('author', ''),
        'url': book_data.get('url', ''),
        'subjects' : csv_row.get('subjects', ''),
        'bookshelves' : csv_row.get('bookshelves', '')
    }

def populate_documents():
    docs = []
    for _, row in tqdm(csv_data.iterrows(), total=csv_data.shape[0]):
        book_id = str(row['book_id'])
        book_data, embedding_data = fetch_book_data(book_id)
        if book_data and embedding_data:
            metadata = create_metadata(book_id, book_data, row)
            embedding = embedding_data['embeddings']

            document = Document(
                page_content=str(embedding),
                metadata=metadata,
                embedding=embedding
            )
            docs.add(document)
            

    try:
        # Initialize vector store
        vector_store = SupabaseVectorStore.from_documents(
            docs,
            embeddings=embedding_function,
            client=supabase,
            table_name="documents",
            query_name="match_documents",
            chunk_size=500,
        )
        #vector_store.add_documents([document])
        print(f"Inserted document for book_id {book_id}")
    except Exception as e:
        print(f"Error inserting document for book_id {book_id}: {e}")

if __name__ == "__main__":
    populate_documents()
