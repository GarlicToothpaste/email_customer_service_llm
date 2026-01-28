from utils.state import EmailAgentState, EmailClassification
from langgraph.types import RetryPolicy
from utils.nodes import read_email , classify_intent,bug_tracking, search_documentation, send_reply
from langgraph.graph import StateGraph, START, END

workflow = StateGraph(EmailAgentState)

workflow.add_node("read_email", read_email)
workflow.add_node("classify_intent", classify_intent)

workflow.add_node("search_documentation", search_documentation,    retry_policy=RetryPolicy(max_attempts=3) )
workflow.add_node("bug_tracking", bug_tracking)
workflow.add_node("send_reply", send_reply)


workflow.add_edge(START, "read_email")
workflow.add_edge("read_email", "classify_intent")
workflow.add_edge("send_reply", END)