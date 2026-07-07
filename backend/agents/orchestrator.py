import os
from typing import TypedDict, Any, Dict, List
from langgraph.graph import StateGraph, END

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

# ==========================================
# 3. Node Implementations
# ==========================================
def extraction_node(state: GraphState) -> GraphState:
    print("Executing: extraction_node")
    transactions = state.get("transactions", [])
    extracted_data = {"status": "success", "data": transactions}
    return {"extracted_data": extracted_data}

def analytics_node(state: GraphState) -> GraphState:
    print("Executing: analytics_node")
    return state

def advisory_node(state: GraphState) -> GraphState:
    print("Executing: advisory_node")
    pref = state.get("user_preference", "buffett")
    system_prompt = PROMPT_TEMPLATES.get(pref, PROMPT_TEMPLATES["buffett"])
    
    current_count = state.get("revision_count", 0)
    # Mock LLM generation guided by persona
    report = f"Draft Report (Revision {current_count}) generated using persona [{pref}]. Guiding philosophy: {system_prompt}"
    return {"advisory_report": report}

def critique_node(state: GraphState) -> GraphState:
    print("Executing: critique_node")
    pref = state.get("user_preference", "buffett")
    # Mock critique evaluating compliance with persona
    print(f"Critique Node evaluating report against strict {pref} financial values...")
    
    current_count = state.get("revision_count", 0)
    return {"revision_count": current_count + 1}

# ==========================================
# 4. Conditional Edges
# ==========================================
def advisory_condition(state: GraphState) -> str:
    count = state.get("revision_count", 0)
    is_flawed = True 
    
    if count >= 3:
        print(f"Critique condition triggered: Exiting to END (Cap reached: {count})")
        return "end"
    elif is_flawed:
        print(f"Critique condition triggered: Routing back to Advisory (Count: {count})")
        return "advisory"
    else:
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

orchestrator_graph = workflow.compile()
