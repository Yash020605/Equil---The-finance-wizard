import io
import os
import json
import logging
import pandas as pd
from langchain_core.tools import tool

# Setup logging for the extraction service
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional imports for OCR libraries
try:
    from google.cloud import vision
except ImportError:
    vision = None

try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None


@tool
def primary_ocr_tool(image_bytes: bytes) -> str:
    """
    Primary OCR Processing using Google Vision API.
    Use this for high-quality extraction of payment screenshots and receipts.
    """
    print("[Primary OCR] Calling Google Vision API for text extraction...")
    
    # 1. Enforce Credential Check
    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        error_msg = "GOOGLE_APPLICATION_CREDENTIALS environment variable is not set."
        logger.error(f"[Primary OCR] {error_msg}")
        raise ValueError(error_msg)
        
    if vision is None:
        raise ImportError("google-cloud-vision library is not installed.")

    try:
        # 2. Initialize Google Vision client and load in-memory buffer
        client = vision.ImageAnnotatorClient()
        image = vision.Image(content=image_bytes)
        
        # 3. Perform text detection
        response = client.text_detection(image=image)
        
        # 4. Error Handling: Rate limits, credential errors, etc.
        if response.error.message:
            error_msg = f"Google Vision API Error: {response.error.message}"
            logger.error(f"[Primary OCR] {error_msg}")
            raise Exception(error_msg)
            
        texts = response.text_annotations
        if texts:
            # The first annotation contains the entire extracted text block
            raw_text = texts[0].description
            print("[Primary OCR] Successfully extracted raw text blocks.")
            
            # Hand raw_text to the LangGraph/Pydantic engine via LLM context
            return json.dumps({
                "extracted_raw_text": raw_text,
                "status": "success",
                "source": "Google Vision API"
            })
        else:
            raise ValueError("No text found in the image by Google Vision.")
            
    except Exception as e:
        logger.error(f"[Primary OCR] Extraction failed: {str(e)}")
        # By raising the exception, the LangGraph extraction_agent_node records a failure
        # and triggers the conditional edge to invoke the Tesseract fallback
        raise


@tool
def secondary_ocr_tool(image_bytes: bytes) -> str:
    """
    Secondary OCR Processing (Fallback) using Tesseract.
    Call this ONLY if the primary OCR fails or returns structurally invalid data.
    """
    print("[Secondary OCR] Fallback to local Tesseract OCR...")
    
    if pytesseract is None or Image is None:
        raise ImportError("pytesseract or Pillow is not installed. Fallback unavailable.")
        
    try:
        # 1. Open the image buffer via Pillow
        image = Image.open(io.BytesIO(image_bytes))
        
        # 2. Execute Tesseract OCR extraction
        raw_text = pytesseract.image_to_string(image)
        
        print("[Secondary OCR] Successfully extracted raw text using Tesseract.")
        
        return json.dumps({
            "extracted_raw_text": raw_text,
            "status": "success",
            "source": "Local Tesseract OCR"
        })
    except Exception as e:
        logger.error(f"[Secondary OCR] Fallback extraction failed: {str(e)}")
        raise


@tool
def csv_parsing_tool(csv_bytes: bytes) -> str:
    """
    CSV and Bank Statement Parsing.
    Use this to extract tabular transaction data from CSV files.
    """
    print("[CSV Parser] Parsing tabular data using Pandas...")
    try:
        # Parse CSV strictly in memory
        df = pd.read_csv(io.BytesIO(csv_bytes))
        return df.to_json(orient="records")
    except Exception as e:
        logger.error(f"[CSV Parser] Error parsing CSV: {str(e)}")
        raise RuntimeError(f"Error parsing CSV: {str(e)}")


# Expose tools for the Extraction Agent
EXTRACTION_TOOLS = [primary_ocr_tool, secondary_ocr_tool, csv_parsing_tool]
