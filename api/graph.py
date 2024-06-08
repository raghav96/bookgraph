import os
from supabase import create_client, Client
from sentence_transformers import SentenceTransformer
from langchain.vectorstores import SupabaseVectorStore
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
client: Client = create_client(supabase_url, supabase_key)

# Initialize embedding function and vector store
embedding_function = SentenceTransformer("all-MiniLM-L6-v2")
docsearch = SupabaseVectorStore(client, table_name="documents", query_name="match_documents", embedding=embedding_function.encode)

def build_graph(source_book_id: str):
    # Fetch top 10 similar books for the source book
    first_level_books = get_similar_books(source_book_id, 10)

    nodes = set()
    edges = []

    # Add source book to nodes
    source_metadata = client.from_('documents').select('metadata').eq('id', source_book_id).single().execute()
    if source_metadata.error:
        raise Exception(f"Error fetching metadata for source book ID {source_book_id}: {source_metadata.error.message}")
    
    nodes.add((source_book_id, source_metadata.data['metadata']))

    for book in first_level_books:
        book_id = book["book_id"]
        similarity = book["similarity_score"]
        metadata = book["metadata"]

        # Add first level book to nodes
        nodes.add((book_id, metadata))
        edges.append({"from": source_book_id, "to": book_id, "weight": similarity})

        # Fetch top 4 similar books for each first level book
        second_level_books = get_similar_books(book_id, 4)

        for second_book in second_level_books:
            second_book_id = second_book["book_id"]
            second_similarity = second_book["similarity_score"]
            second_metadata = second_book["metadata"]

            # Add second level book to nodes
            nodes.add((second_book_id, second_metadata))
            edges.append({"from": book_id, "to": second_book_id, "weight": second_similarity})

    nodes = [{"id": node[0], "label": node[1]['title']} for node in nodes]
    return {"nodes": nodes, "edges": edges}

def get_similar_books(book_id: str, top_n: int):
    # Fetch the embedding for the book_id
    response = client.from_('book_embeddings').select('embeddings').eq('book_id', book_id).single().execute()
    if response.error or not response.data:
        raise Exception(f"Error fetching embedding for book ID {book_id}: {response.error.message}")

    embedding = response.data['embeddings']

    # Perform similarity search
    relevant_docs = docsearch.similarity_search_by_vector_with_relevance_scores(embedding, k=top_n)
    return [{"book_id": doc.metadata["book_id"], "similarity_score": doc.similarity, "metadata": doc.metadata} for doc in relevant_docs]
