from utils.rag_functions import initialize_llm, initialize_vectorstore, query_rag
# from langchain.tools import tool

import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.engine import URL
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

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

def create_ticket(description : str):
    """Adds an ticket to the database"""
    message = ""
    try:
        with engine.connect() as connection:

            status = "TICKET_CREATED"
            sql_statement = text(f"INSERT INTO customer_tickets ( description, status) VALUES ( :description, :status)")
            result = connection.execute(sql_statement, { "description" : description, "status": status})
            connection.commit()
            
            
            ticket_id = result.lastrowid
            message = f"{ticket_id}"
    except Exception as e:
        print(f"Connection failed: {e}")
    return(message)

def retrieve_ticket(ticket_id : str):
    """Gets the status of a ticket"""
    message = ""
    try:
        with engine.connect() as connection:
            sql_statement = text(f"SELECT status FROM customer_tickets WHERE ticket_id = :ticket_id")
            result = connection.execute(sql_statement, {"ticket_id" : ticket_id})
            
            row = result.fetchone()
            
            if row:
                status = row[0]
                message = f'Current status of  ticket {ticket_id}: {status}'
            
            else:
                # message = f'Ticket ID {ticket_id} not found'
                message = "Ticket Not Found"
    except Exception as e:
        print(f"Connection failed: {e}")
    return(message)
 
# print(retrieve_ticket("5"))