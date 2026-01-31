from utils.rag_functions import initialize_llm, initialize_vectorstore, query_rag
# from langchain.tools import tool

llm = initialize_llm()
vectorstore = initialize_vectorstore()

def send_email():
    print ("Test")

def get_documentation(question: str):
    """Gets information based on a question"""
    response = query_rag(question=question, vectorstore=vectorstore,llm=llm)
    return response

def create_ticket():
    print("Test")

def retrieve_ticket():
    print("Test")