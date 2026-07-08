import os
import sys
import pandas as pd
from typing import TypedDict, Any, Dict, List
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db import checkpointer
from agents.llm import llm

# ==========================================
# 1. Prompts & Templates
# ==========================================
PROMPT_TEMPLATES = {
    "buffett": "You are Warren Buffett. Focus on value investing, long-term fundamentals, and buying strong companies at a discount. Ignore short-term market noise.",
    "fire": "You are a F.I.R.E. (Financial Independence, Retire Early) advocate. Focus on aggressive savings rates, minimizing expenses, and maximizing index fund contributions.",
    "kiyosaki": "You are Robert Kiyosaki. Focus on cash-flowing assets, real estate, minimizing taxes, and distinguishing between liabilities and true assets."
}

# ==========================================
# 2. State Definition
# ==========================================
class GraphState(TypedDict):
    transactions: List[Dict[str, Any]]
    extracted_data: Dict[str, Any]
    advisory_report: str
    revision_count: int
    user_preference: str
    is_flawed: bool

# Output model for Critique Node
class CritiqueOutput(BaseModel):
    is_flawed: bool = Field(description="True if the advisory report is generic or violates the persona's philosophy. False otherwise.")
    feedback: str = Field(description="Critique notes explaining why.")

# ==========================================
# 3. Node Implementations
# ==========================================
def extraction_node(state: GraphState) -> GraphState:
    print("Executing: extraction_node (Validator)")
    transactions = state.get("transactions", [])
    
    # Simple validation: ensure JSON isn't empty
    status = "success" if len(transactions) > 0 else "failed_validation"
    return {"extracted_data": {"status": status, "data": transactions}}

def analytics_node(state: GraphState) -> GraphState:
    print("Executing: analytics_node")
    transactions = state.get("transactions", [])
    if not transactions:
        return state
        
    # Tool Binding: Pandas
    df = pd.DataFrame(transactions)
    summary = df.groupby("category")["amount"].sum().to_dict()
    print(f"Pandas Analytics Summary: {summary}")
    
    # Attach the summary back into state
    extracted_data = state.get("extracted_data", {})
    extracted_data["summary"] = summary
    return {"extracted_data": extracted_data}

def advisory_node(state: GraphState) -> GraphState:
    print("Executing: advisory_node")
    pref = state.get("user_preference", "buffett")
    system_prompt = PROMPT_TEMPLATES.get(pref, PROMPT_TEMPLATES["buffett"])
    
    # Prepare LLM Chain
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Here is the transaction summary from Pandas: {summary}\nGenerate a personalized advisory report based on your strict philosophy.")
    ])
    
    summary = state.get("extracted_data", {}).get("summary", {})
    chain = prompt | llm
    
    # LLM Invocation
    response = chain.invoke({"summary": summary})
    
    current_count = state.get("revision_count", 0)
    print(f"Advisory Generation complete (Revision {current_count})")
    
    return {"advisory_report": response.content}

def critique_node(state: GraphState) -> GraphState:
    print("Executing: critique_node")
    pref = state.get("user_preference", "buffett")
    report = state.get("advisory_report", "")
    
    # Prepare Critique LLM Chain
    critique_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an elite financial auditor. Evaluate the following advisory report. "
                   f"Does it strictly adhere to the '{pref}' philosophy? Be harsh. If it is generic, mark it flawed."),
        ("human", "Report to evaluate:\n{report}")
    ])
    
    structured_llm = llm.with_structured_output(CritiqueOutput)
    chain = critique_prompt | structured_llm
    
    critique = chain.invoke({"report": report})
    print(f"Critique Output: Flawed={critique.is_flawed}, Feedback={critique.feedback}")
    
    current_count = state.get("revision_count", 0)
    return {
        "revision_count": current_count + 1,
        "is_flawed": critique.is_flawed
    }

# ==========================================
# 4. Conditional Edges
# ==========================================
def advisory_condition(state: GraphState) -> str:
    count = state.get("revision_count", 0)
    is_flawed = state.get("is_flawed", False)
    
    if count >= 3:
        print(f"Critique condition triggered: Exiting to END (Cap reached: {count})")
        return "end"
    elif is_flawed:
        print(f"Critique condition triggered: Routing back to Advisory (Count: {count})")
        return "advisory"
    else:
        print(f"Critique condition triggered: Report passed! Exiting to END.")
        return "end"

# ==========================================
# 5. Graph Construction
# ==========================================
workflow = StateGraph(GraphState)

workflow.add_node("extraction", extraction_node)
workflow.add_node("analytics", analytics_node)
workflow.add_node("advisory", advisory_node)
workflow.add_node("critique", critique_node)

workflow.set_entry_point("extraction")
workflow.add_edge("extraction", "analytics")
workflow.add_edge("analytics", "advisory")
workflow.add_edge("advisory", "critique")

workflow.add_conditional_edges(
    "critique",
    advisory_condition,
    {
        "advisory": "advisory",
        "end": END
    }
)

orchestrator_graph = workflow.compile(checkpointer=checkpointer)
