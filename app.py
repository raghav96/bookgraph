import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from supabase import create_client, Client
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.vectorstores import SupabaseVectorStore
from api.search import get_top_books

load_dotenv()

app = Flask(__name__)

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
client: Client = create_client(supabase_url, supabase_key)

# Initialize embedding function and vector store
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
docsearch = SupabaseVectorStore(client, table_name="book_embeddings", embedding_function=embedding_function)

@app.route('/search', methods=['POST'])
def search():
    user_question = request.json.get('question')
    if user_question:
        top_books = get_top_books(user_question, docsearch)
        return jsonify({"top_books": top_books})
    return jsonify({"error": "No question provided"}), 400

if __name__ == "__main__":
    app.run(port=5000, debug=True)
