from rag_functions import initialize_llm, initialize_vectorstore, query_rag
from langchain.tools import tool

llm = initialize_llm()
vectorstore = initialize_vectorstore()

@tool
def send_email():
    print ("Test")

@tool
def get_documentation(question: str):
    response = query_rag(question=question, vectorstore=vectorstore,llm=llm)
    return response

@tool
def create_ticket():
    print("Test")

@tool
def retrieve_ticket():
    print("Test")