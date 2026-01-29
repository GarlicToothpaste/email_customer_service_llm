from rag_functions import initialize_llm, initialize_vectorstore, query_rag

llm = initialize_llm()
vectorstore = initialize_vectorstore()

def send_email():
    print ("Test")

def get_documentation(question: str):
    query_rag(question=question, vectorstore=vectorstore,llm=llm)

def create_ticket():
    print("Test")

def retrieve_ticket():
    print("Test")