from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from pathlib import Path
# from populate_db import index_folder

WATCH_PATH = Path("./knowledge_base")
DB_PATH = "./chroma_db"
MODEL_NAME = "qwen3:4b"
EMBED_MODEL = "nomic-embed-text:latest"

def initialize_llm():
    """Initializes the LLM"""
    llm = ChatOllama(model=MODEL_NAME, temperature = 0.7)
    
    return llm

def initialize_vectorstore():
    """Initializes the Vectorstore"""
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)

    vectorstore = Chroma(
        persist_directory = str(DB_PATH),
        embedding_function = embeddings,
        collection_name = "documents"
    )

    return vectorstore

def query_rag(question : str, vectorstore , llm):
    """Retrieves from the DB to generate answers"""

    docs = vectorstore.similarity_search(question, k=5)

    if not docs:
        return "No documents found for your question"
    
    context = "\n\n---\n\n".join([d.page_content for d in docs])

    prompt_template = f"""
    You are an customer service agent that helps people with a product with given context from a manual.

    Given this context: {context}

    Make a summary that answers this question: {question}
    """

    response = llm.invoke(prompt_template)
    return response.content.strip()
