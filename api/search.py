from langchain.vectorstores import SupabaseVectorStore
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings

def get_top_books(user_question, docsearch: SupabaseVectorStore, top_n=10):
    relevant_docs = docsearch.similarity_search(user_question, k=top_n)
    return [{"title": doc.metadata["title"], "content": doc.page_content} for doc in relevant_docs]
