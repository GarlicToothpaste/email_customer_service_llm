from langchain_ollama import ChatOllama
from langchain.messages import HumanMessage
from langgraph.types import interrupt, Command, RetryPolicy
from typing import Literal
from langgraph.graph import END
from utils.tools import get_documentation, create_ticket,retrieve_ticket

from utils.state import EmailAgentState, EmailClassification

llm = ChatOllama(
    model="qwen3:4b",
    temperature=0.7
)

def read_email (state : EmailAgentState):
    """LLM Reads the Email Given by the User"""

    return {
        "messages": HumanMessage(content=f"Processing email: {state['email_content']}")
    }

def classify_intent(state : EmailAgentState) -> Command[Literal["search_documentation", "human_review", "draft_response", "bug_tracking"]]:
    """Use LLM to classify email intent and urgency, then route accordingly"""

    structured_llm = llm.with_structured_output(EmailClassification)

    classification_prompt = f"""
    Analyze this customer email and classify it:

    Email: {state['email_content']}
    From: {state['sender_email']}

    Provide classification including intent, urgency, topic, and summary.
    """

    classification = structured_llm.invoke(classification_prompt)

    if classification['intent'] == 'billing' or classification['urgency'] == 'critical':
        goto = "human_review"
    elif classification['intent'] in ['question', 'feature']:
        goto = "search_documentation"
    elif classification['intent'] == 'bug':
        goto = "bug_tracking"
    else:
        goto = "draft_response"

    return Command(
        update={"classification": classification},
        goto=goto
    )

def search_documentation(state : EmailAgentState) -> Command[Literal["draft_response"]]:
    """Searches knowledge base for information"""

    # Returns {} when there is no classification
    classification = state.get('classification' , {})
    query = f"{classification.get('intent', '')} {classification.get('topic', '')}"
    question = state.get('email_content')
    try:
        search_results = get_documentation(question=question)

    except Exception as e:
        search_results = [f"Search temporarily unavailable: {str(e)}"]
    
    return Command(
        update={"search_results": search_results},
        goto="draft_response"
    )

def identify_ticket(state:EmailAgentState) -> Command[Literal['retrieve_bug_tracking_ticket' , 'create_bug_tracking_ticket']]:
    #TODO: Add Structure
    bug_prompt = f"""
    You are an AI that helps categorize customer tickets.

    Given this email:
    {state['email_content']}

    Determine if the user wants to create a ticket or retrieve a previously created one
    """

def retrieve_bug_tracking_ticket(state: EmailAgentState) -> Command[Literal["draft_response"]]:
    """Retrieves a bug report ticket"""
    bug_prompt = f"""
    You are an AI that helps retrieve customer service emails. 
    
    Given this email:
    {state['email_content']}

    Get the ticket ID only provided by the customer.
    """
    response = llm.invoke(bug_prompt)

    response = retrieve_ticket(response)
    return Command(
        update = {
            "search_results": response,
            "current_step" : "retrieved_bug_tracking_ticket"

        }, goto=draft_response
    )

def create_bug_tracking_ticket(state : EmailAgentState) -> Command[Literal["draft_response"]]:
    """Creates a bug report ticket"""
    bug_prompt = f"""
    You are an AI that helps summarize emails for a ticketing system. 
    
    Given this email:
    {state['email_content']}

    Make a summary of their issue in 225 Characters or less.
    """

    response = llm.invoke(bug_prompt)

    ticket_id = create_ticket(response)

    return Command(
        update={
            "search_results" : [f"Bug Ticket with {ticket_id} created"],
            "current_step" : "created_bug_tracking_ticket"
        },
        goto = "draft_response"
    )

def draft_response(state: EmailAgentState) -> Command[Literal['human_review', "send_reply"]]:

    classification = state.get('classification', {})

    context_sections = []

    if state.get('search_results'):
        formatted_docs = "\n".join([f"- {doc}" for doc in state['search_results']])
        context_sections.append(f"Relevant documentation:\n{formatted_docs}")

    if state.get('customer_history'):
        context_sections.append(f"Customer tier: {state['customer_history'].get('tier', 'standard')}")

    draft_prompt = f"""
    Draft a response to this customer email:
    {state['email_content']}

    Email intent: {classification.get('intent', 'unknown')}
    Urgency level: {classification.get('urgency', 'medium')}

    {chr(10).join(context_sections)}

    Guidelines:
    - Be professional and helpful
    - Address their specific concern
    - Use the provided documentation when relevant
    - The message you will draft will be sent as a reply to the customer
    """

    response = llm.invoke(draft_prompt)

    # Determine if human review needed based on urgency and intent
    needs_review = (
        classification.get('urgency') in ['high', 'critical'] or
        classification.get('intent') == 'complex'
    )

    # Route to appropriate next node
    goto = "human_review" if needs_review else "send_reply"

    return Command(
        update={"draft_response": response.content},  # Store only the raw response
        goto=goto
    )

def human_review (state: EmailAgentState):
    """Pause for human review using interrupt and route based on human decision"""

    classification = state.get('classification')

    human_decision = interrupt({
        "email_id" : state.get("email_id", ''),
        "email_content" : state.get("email_content", ''),
        "draft_response" : state.get("draft_response", ''),
        "urgency" : classification.get("urgency" , ''),
        "intent" : classification.get("intent" , ''),
        "action" : "Please review and approve this response"
    })

    if human_decision.get("approved"):
        return Command (
            update = {"draft_response" : human_decision.get(("edited_response"), state.get("draft_response"))},
            goto = "send_reply"
        )
    
    else:
        rejection=  Command(update = {}, goto=END)


def send_reply (state: EmailAgentState):
    """Send Email Response"""

    print(f"Sending the reply: {state['draft_response']}")

    return {"draft_response" : state['draft_response']}
