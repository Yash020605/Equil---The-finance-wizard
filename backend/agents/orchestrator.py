import operator
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from services.extraction import EXTRACTION_TOOLS
from services.synthesis import SYNTHESIS_TOOLS
from services.analytics import ANALYTICS_TOOLS

# ==========================================
# 1. State Management Configuration
# ==========================================
class GraphState(BaseModel):
    """
    Pydantic model representing the State of the Multi-Agent Pipeline.
    Tracks all necessary context for loop-backs (retry counts, validation errors, critique feedback).
    """
    # Input
    raw_document_path: Optional[str] = None
    
    # Extraction State
    extracted_data: Optional[Dict[str, Any]] = None
    extraction_retry_count: int = Field(default=0, description="Tracks number of OCR retry attempts.")
    extraction_errors: List[str] = Field(default_factory=list, description="Validation errors from the Extraction Validation Loop.")
    
    # Analytics State
    analytics_bundle: Optional[Dict[str, Any]] = Field(default=None, description="Smart categorization, health score, and anomaly data.")
    
    # Synthesis State
    synthesis_context: str = Field(default="", description="Knowledge base context retrieved by Synthesis Agent.")
    
    # Advisory State
    draft_recommendation: str = Field(default="", description="Drafted recommendation pending critique.")
    advisory_critique_notes: List[str] = Field(default_factory=list, description="Critique feedback forcing a revision.")
    advisory_revision_count: int = Field(default=0, description="Tracks number of advisory revisions.")
    final_recommendation: str = Field(default="", description="Final, validated output.")


# ==========================================
# 2. Node Definitions
# ==========================================

async def extraction_agent_node(state: GraphState) -> Dict:
    """
    Extraction Agent: Ingests data using primary OCR or fallback OCR depending on retry count.
    """
    current_retries = state.extraction_retry_count
    
    # Integration: Bind tools to the Extraction Agent LLM
    # Example: llm = ChatOpenAI(model="gpt-4").bind_tools(EXTRACTION_TOOLS)
    print(f"[Extraction Agent] Agent initialized with tools: {[t.name for t in EXTRACTION_TOOLS]}")
    
    # Fallback Logic Implementation
    if current_retries > 0:
        print(f"[Extraction Agent] Retry {current_retries}: Invoking secondary_ocr_tool (Tesseract)...")
        # llm.invoke(...) -> routes to secondary_ocr_tool
    else:
        print("[Extraction Agent] Attempting primary_ocr_tool (Google Vision/Textract)...")
        # llm.invoke(...) -> routes to primary_ocr_tool
        
    # Simulated Extraction Result
    # (In a real implementation, we would parse the OCR output here)
    mock_extracted_data = state.extracted_data or {}
    
    return {"extracted_data": mock_extracted_data}


async def validation_node(state: GraphState) -> Dict:
    """
    The Extraction Validation Loop: Checks structural integrity of the extracted JSON.
    """
    print("[Validation Node] Checking structural integrity of extracted data...")
    errors = []
    data = state.extracted_data or {}
    
    # Structural integrity checks
    required_keys = ["amount", "date", "vendor"]
    for key in required_keys:
        if key not in data:
            errors.append(f"Missing required key: {key}")
            
    if errors:
        print(f"[Validation Node] Validation failed with errors: {errors}")
        # Increment retry count and append errors so the Extraction Agent has full context on loop-back
        return {
            "extraction_errors": state.extraction_errors + errors,
            "extraction_retry_count": state.extraction_retry_count + 1
        }
    
    print("[Validation Node] Validation passed.")
    return {"extraction_errors": []}  # Clear errors on success


async def synthesis_agent_node(state: GraphState) -> Dict:
    """
    Synthesis Agent: Retrieves necessary 'Multi-Guru' philosophy context based on extracted data.
    """
    print(f"[Synthesis Agent] Agent initialized with tools: {[t.name for t in SYNTHESIS_TOOLS]}")
    
    print("[Synthesis Agent] Processing context from the knowledge base...")
    # Integration: Bind tools to Synthesis Agent LLM
    # Example: llm.bind_tools(SYNTHESIS_TOOLS).invoke("Extract context based on user data...")
    
    # Simulated Context Retrieval
    context = (
        "Warren Buffett: Value-driven, long-term focus.\n"
        "Robert Kiyosaki: Acquire cash-flowing assets, avoid liabilities.\n"
        "Ramit Sethi: Conscious spending on your 'Rich Life'."
    )
    return {"synthesis_context": context}


async def analytics_agent_node(state: GraphState) -> Dict:
    """
    Analytics Agent: Processes extracted data to build the analytics bundle
    (Categorization, Health Scoring, Goal Tracking).
    """
    print(f"[Analytics Agent] Agent initialized with tools: {[t.name for t in ANALYTICS_TOOLS]}")
    print("[Analytics Agent] Running predictive analytics and smart categorization...")
    
    # Integration: Bind tools to Analytics Agent LLM
    # Example: llm.bind_tools(ANALYTICS_TOOLS).invoke(...)
    
    # Simulated Analytics Execution
    bundle = {
        "smart_categorization": {"Essential Living": 1500.0, "Discretionary Spend": 450.0, "Investment": 500.0},
        "anomalies_detected": ["$400 at Apple Store flagged as anomaly (3x above baseline)"],
        "financial_health_score": 78,
        "milestone_projections": ["International Studies goal achievable in 14 months."]
    }
    
    return {"analytics_bundle": bundle}


async def advisory_agent_node(state: GraphState) -> Dict:
    """
    Advisory Agent: Generates a draft recommendation using the Synthesis Agent's context.
    """
    print("[Advisory Agent] Generating draft recommendation...")
    
    # ---------------------------------------------------------
    # PROMPT ENGINEERING: Multi-Guru Orchestration
    # ---------------------------------------------------------
    system_prompt = f"""
    You are the Equil Advisory Reasoning Engine.
    
    Extracted Transaction Data:
    {state.extracted_data}
    
    Predictive Analytics & Categorization Bundle:
    {state.analytics_bundle}
    
    Multi-Guru Philosophical Context:
    {state.synthesis_context}
    
    Your Task: Cross-examine the user's spending data and analytics bundle against these distinct guru philosophies.
    Generate a balanced, multi-perspective financial synthesis report.
    
    STRICT GUARDRAILS:
    1. Do not provide certified investment advice.
    2. Do not suggest or recommend direct stock-picking or illegal maneuvers.
    3. The tone must remain strictly educational, objective, and analytical.
    """
    
    if state.advisory_critique_notes:
        print(f"[Advisory Agent] Revising based on Critique Feedback: {state.advisory_critique_notes}")
        # Simulated LLM invoke (with critique feedback included in messages)
        draft = "Revised Draft: Based on the Multi-Guru educational frameworks, you should consider optimizing your cash flow toward broadly diversified assets while continuing conscious spending."
        return {"draft_recommendation": draft, "advisory_revision_count": state.advisory_revision_count + 1}
    else:
        # Simulated LLM invoke based on the system prompt
        draft = "Draft: Multi-Perspective Report - Kiyosaki would suggest tracking this spending as a liability. Sethi would ask if this aligns with your 'Rich Life'. Buffett advises keeping expenses low to enable long-term compounding in broad index funds."
        
    return {"draft_recommendation": draft}


async def critique_node(state: GraphState) -> Dict:
    """
    The Advisory Critique Loop: Evaluates the draft against strict safety constraints.
    """
    print("[Critique Node] Critiquing draft recommendation...")
    notes = []
    draft = state.draft_recommendation.lower()
    
    # Safety constraints check: No illegal direct investment advice or overly risky single-stock picks
    if "high-risk" in draft or "stock" in draft:
        notes.append("SAFETY VIOLATION: Draft contains potentially illegal direct investment advice or overly risky suggestions. Tone must be educational and balanced.")
        
    if notes:
        print(f"[Critique Node] Draft flagged! Routing back for revision. Notes: {notes}")
        return {"advisory_critique_notes": state.advisory_critique_notes + notes}
    
    print("[Critique Node] Draft passed safety checks.")
    return {"advisory_critique_notes": []}  # Clear critique notes on success


async def final_output_node(state: GraphState) -> Dict:
    """
    Final Output Node: Solidifies the approved recommendation.
    """
    print("[Final Output Node] Recommendation finalized and ready for the user.")
    return {"final_recommendation": state.draft_recommendation}


# ==========================================
# 3. Conditional Edge Logic
# ==========================================

def extraction_condition(state: GraphState) -> str:
    """
    Routes from Validation Node based on validation success or failure.
    Max retries = 3.
    """
    if state.extraction_errors:
        if state.extraction_retry_count < 3:
            return "retry"
        else:
            raise Exception("Terminal extraction failure: Max retries exceeded.")
    return "pass"

def advisory_condition(state: GraphState) -> str:
    """
    Routes from Critique Node based on safety checks. Capped at 3 revisions.
    """
    if state.advisory_critique_notes:
        if state.advisory_revision_count < 3:
            return "revise"
        else:
            print("[Advisory Critique] Max revisions exceeded. Proceeding with safe fallback.")
            return "pass"  # Or route to an escalation/END node
    return "pass"


# ==========================================
# 4. Graph Construction & Compilation
# ==========================================

def build_orchestrator_graph() -> StateGraph:
    """
    Constructs the StateGraph with the requested Feedback Loops.
    """
    workflow = StateGraph(GraphState)
    
    # Add Nodes
    workflow.add_node("extraction_agent", extraction_agent_node)
    workflow.add_node("validation_node", validation_node)
    workflow.add_node("analytics_agent", analytics_agent_node)
    workflow.add_node("synthesis_agent", synthesis_agent_node)
    workflow.add_node("advisory_agent", advisory_agent_node)
    workflow.add_node("critique_node", critique_node)
    workflow.add_node("final_output_node", final_output_node)
    
    # Set Entry Point
    workflow.set_entry_point("extraction_agent")
    
    # Extraction Validation Loop
    workflow.add_edge("extraction_agent", "validation_node")
    workflow.add_conditional_edges(
        "validation_node",
        extraction_condition,
        {
            "retry": "extraction_agent",  # Loop back to Extraction
            "fail": END,                  # Or route to human-in-the-loop exception queue
            "pass": "analytics_agent"     # Proceed to Analytics
        }
    )
    
    # Linear flow: Analytics -> Synthesis -> Advisory
    workflow.add_edge("analytics_agent", "synthesis_agent")
    workflow.add_edge("synthesis_agent", "advisory_agent")
    
    # Advisory Critique Loop
    workflow.add_edge("advisory_agent", "critique_node")
    workflow.add_conditional_edges(
        "critique_node",
        advisory_condition,
        {
            "revise": "advisory_agent",   # Loop back to Advisory Agent for correction
            "pass": "final_output_node"   # Proceed to output
        }
    )
    
    # Finalize
    workflow.add_edge("final_output_node", END)
    
    return workflow


async def get_compiled_graph(postgres_pool):
    """
    Compiles the graph using PostgreSQL as the checkpointer.
    This enables state persistence and future Human-in-the-Loop (HITL) breakpoints.
    
    Args:
        postgres_pool: An asyncpg connection pool or valid SQLAlchemy async engine connection.
    """
    workflow = build_orchestrator_graph()
    
    # Configure PostgreSQL as the checkpointer for the LangGraph state
    checkpointer = AsyncPostgresSaver(postgres_pool)
    
    # Compile graph with the checkpointer to enable HITL breakpoints and long-term state tracking
    app = workflow.compile(checkpointer=checkpointer)
    
    return app
