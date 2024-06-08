import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from supabase import create_client, Client
from sentence_transformers import SentenceTransformer
from langchain_core.documents import Document
from langchain_community.vectorstores import SupabaseVectorStore
from api.search import get_top_books
from api.graph import build_graph

load_dotenv()

app = Flask(__name__)

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
client: Client = create_client(supabase_url, supabase_key)

# Initialize embedding function and vector store
embedding_function = SentenceTransformer("all-MiniLM-L6-v2")
docsearch = SupabaseVectorStore(client, table_name="documents", query_name="match_documents", embedding=embedding_function.encode)

@app.route('/search', methods=['POST'])
def search():
    user_question = request.json.get('question')
    if user_question:
        top_books = get_top_books(user_question, docsearch)
        return jsonify({"top_books": top_books})
    return jsonify({"error": "No question provided"}), 400

@app.route('/graph', methods=['GET'])
def graph():
    book_id = request.args.get('book_id')
    if not book_id:
        return jsonify({"error": "Missing book_id parameter"}), 400

    try:
        graph = build_graph(book_id)
        return jsonify(graph)
    except Exception as e:
        return jsonify({"error": f"Failed to build graph: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
