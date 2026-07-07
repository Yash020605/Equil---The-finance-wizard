import io
import json
from langchain_core.tools import tool

# Assuming PyPDF2 is installed in the environment (e.g., via uv or pip)
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

@tool
def pdf_document_processing_tool(pdf_bytes: bytes) -> str:
    """
    Document Processing Tool: Extracts and chunks text from uploaded financial literature PDFs.
    """
    print("[Document Processing Tool] Extracting text from PDF...")
    if PyPDF2 is None:
        raise RuntimeError("PyPDF2 is not installed. Unable to process PDF.")
        
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        extracted_text = ""
        for page in reader.pages:
            extracted_text += page.extract_text() + "\n"
        
        # Sliding-window chunking strategy to preserve RAG context
        chunk_size = 1500
        overlap = 200
        chunks = []
        start = 0
        while start < len(extracted_text):
            end = start + chunk_size
            chunks.append(extracted_text[start:end])
            start += chunk_size - overlap
            
        return json.dumps({"chunks": chunks})
    except Exception as e:
        raise RuntimeError(f"Error parsing PDF: {str(e)}")

@tool
def guru_strategy_mapper_tool(query: str) -> str:
    """
    Guru Strategy Mapper: Retrieves core financial paradigms based on the topic.
    Provides perspectives from Warren Buffett, Robert Kiyosaki, and Ramit Sethi.
    """
    print(f"[Guru Strategy Mapper] Retrieving paradigms for query: {query}")
    
    paradigms = {
        "Warren Buffett": "Value-driven, long-term approach. Focus on underlying business fundamentals, low fees, and compounding.",
        "Robert Kiyosaki": "Asset vs. Liability tracking. Emphasizes building passive income through cash-flowing assets rather than saving cash.",
        "Ramit Sethi": "'Rich Life' conscious spending. Automate finances, cut costs mercilessly on things you don't care about, and spend extravagantly on things you love."
    }
    
    # Format the retrieved paradigms for the LLM context window
    retrieved_context = "Multi-Guru Financial Paradigms:\n"
    for guru, strategy in paradigms.items():
        retrieved_context += f"- {guru}: {strategy}\n"
        
    return retrieved_context

# Expose tools for the Synthesis Agent
SYNTHESIS_TOOLS = [pdf_document_processing_tool, guru_strategy_mapper_tool]
