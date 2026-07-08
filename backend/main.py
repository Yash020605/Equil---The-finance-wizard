import ctypes
import gc
import uuid
import json
from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from db import initialize_db, checkpointer
from agents.orchestrator import orchestrator_graph

try:
    import magic
except ImportError:
    magic = None

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Equil Backend")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "application/pdf", "text/csv"}

def run_vision_extraction(file_bytes: bytearray) -> list:
    """
    Mock Google Cloud Vision extraction.
    In production, this would send the bytes to the Vision API,
    parse the OCR layout into structured JSON, and return a list of dicts.
    """
    return [
        {"date": "2026-07-01", "description": "ACH DEBIT - Robinhood", "amount": -500.00, "category": "Investment"},
        {"date": "2026-07-03", "description": "STARBUCKS STORE", "amount": -12.50, "category": "Food"},
        {"date": "2026-07-05", "description": "DIRECT DEP - PAYROLL", "amount": 4200.00, "category": "Income"}
    ]

@app.on_event("startup")
async def startup_event():
    await initialize_db()

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.post("/api/v1/extract/upload")
@limiter.limit("10/minute")
async def upload_document(
    request: Request, 
    file: UploadFile = File(...),
    user_preference: str = Form("buffett")
):
    raw_content = await file.read()
    
    # Hard cap 20MB
    if len(raw_content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Payload Too Large")

    # MIME Validation via python-magic
    if magic:
        mime_type = magic.from_buffer(raw_content, mime=True)
        if mime_type not in ALLOWED_MIME_TYPES and not (mime_type == "text/plain" and file.filename.endswith(".csv")):
            raise HTTPException(status_code=415, detail=f"Unsupported Media Type: {mime_type}")
    
    # Isolate memory into mutable bytearray
    file_buffer = bytearray(raw_content)
    
    try:
        # Pre-Graph Extraction: Extract structured JSON while bytes exist
        structured_json = run_vision_extraction(file_buffer)
        session_id = str(uuid.uuid4())
        
        # Zero-Trust memory wipe *before* Graph entry
        char_array = (ctypes.c_char * len(file_buffer)).from_buffer(file_buffer)
        ctypes.memset(ctypes.addressof(char_array), 0, len(file_buffer))
        del file_buffer
        del raw_content
        gc.collect()

        print(f"Graph Logic Routed to Persona: {user_preference} [Session: {session_id}]")
        
        # Open checkpointer context manager and invoke graph
        async with checkpointer:
            await orchestrator_graph.ainvoke(
                {"user_preference": user_preference, "transactions": structured_json, "revision_count": 0},
                config={"configurable": {"thread_id": session_id}}
            )
        
        return {
            "status": "success",
            "message": "File ingested securely and memory wiped.",
            "persona_routed": user_preference,
            "session_id": session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
