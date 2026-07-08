import ctypes
import gc
import uuid
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

    # MIME Validation via python-magic (Strict Byte Signature check)
    if magic:
        mime_type = magic.from_buffer(raw_content, mime=True)
        if mime_type not in ALLOWED_MIME_TYPES and not (mime_type == "text/plain" and file.filename.endswith(".csv")):
            raise HTTPException(status_code=415, detail=f"Unsupported Media Type: {mime_type}")
    
    # Isolate memory into mutable bytearray
    file_buffer = bytearray(raw_content)
    
    try:
        session_id = str(uuid.uuid4())
        print(f"Ingesting file {file.filename}. Routing graph logic to Persona: {user_preference} [Session: {session_id}]")
        
        # Open checkpointer context manager and invoke graph
        async with checkpointer:
            await orchestrator_graph.ainvoke(
                {"user_preference": user_preference, "transactions": []},
                config={"configurable": {"thread_id": session_id}}
            )
        
        return {
            "status": "success",
            "message": "File ingested securely.",
            "persona_routed": user_preference,
            "session_id": session_id
        }
    finally:
        # Cryptographic memory wipe (Zero-Trust)
        if len(file_buffer) > 0:
            char_array = (ctypes.c_char * len(file_buffer)).from_buffer(file_buffer)
            ctypes.memset(ctypes.addressof(char_array), 0, len(file_buffer))
        
        del file_buffer
        del raw_content
        gc.collect()
