from utils.rag_functions import initialize_llm, initialize_vectorstore, query_rag
# from langchain.tools import tool

import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.engine import URL
from sqlalchemy import create_engine, text


load_dotenv()  

db_type = os.environ.get("DB_TYPE") 
driver = os.environ.get("DB_DRIVER")
username = os.environ.get("DB_USERNAME")
password = os.environ.get("DB_PASSWORD")
host = os.environ.get("DB_HOST")
database = os.environ.get("DATABASE")
port = os.environ.get("PORT") # Optional, defaults are often fine

if driver:
    drivername = f"{db_type}+{driver}"
else:
    drivername = db_type

DATABASE_URL = URL.create(
    drivername=drivername,
    username=username,
    password=password,
    host=host,
    database=database,
    port=port,
)

engine = create_engine(DATABASE_URL, echo=True) 


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