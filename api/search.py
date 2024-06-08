from langchain.vectorstores import SupabaseVectorStore

def get_top_books(user_question, docsearch: SupabaseVectorStore, top_n=10):
    relevant_docs = docsearch.similarity_search(user_question, k=top_n)
    return [{"book_id": doc.metadata["book_id"], "metadata": doc.metadata} for doc in relevant_docs]
