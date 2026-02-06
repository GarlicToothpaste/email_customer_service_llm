from typing_extensions import TypedDict, Literal

class EmailClassification(TypedDict):
    intent: Literal["question", "bug", "billing", "feature", "complex"]
    urgency: Literal["low", "medium", "high", "critical"]
    topic : str 
    summary : str 

class TicketClassification(TypedDict):
    intent: Literal['create_ticket', 'retrieve_ticket']

class EmailAgentState(TypedDict):
    email_content: str
    sender_email:str
    email_id : str 

    classification : EmailClassification | None 
    ticket_classification: TicketClassification | None

    search_results : list[str] | None
    customer_history : dict | None 

    draft_response : str | None 
    messages : list[str] | None