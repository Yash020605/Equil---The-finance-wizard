import ctypes
import gc
import uuid
import io
import os
import re
import json
import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from db import initialize_db, get_postgres_checkpointer
from agents.orchestrator import orchestrator_graph

try:
    import magic
except ImportError:
    magic = None

try:
    import pytesseract
    from PIL import Image as PILImage
except ImportError:
    pytesseract = None
    PILImage = None

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import docx
except ImportError:
    docx = None

import pandas as pd

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Equil Backend")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

MAX_UPLOAD_BYTES = int(os.environ.get("MAX_UPLOAD_BYTES", 20 * 1024 * 1024))

ALLOWED_MIME_TYPES = {
    "image/png", "image/jpeg", "image/webp",
    "application/pdf",
    "text/csv", "text/plain",
    "application/octet-stream",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

# ─────────────────────────────────────────────────────────────────────────────
# SMART CATEGORISATION ENGINE
# Keyword → category mapping. Checked in order; first match wins.
# ─────────────────────────────────────────────────────────────────────────────
CATEGORY_RULES: list[tuple[str, list[str]]] = [
    # Income signals
    ("Income", [
        "salary", "payroll", "direct dep", "direct deposit", "wage",
        "freelance", "consulting fee", "invoice payment", "client payment",
        "revenue", "refund", "cashback", "interest earned", "dividend",
    ]),
    # Investment
    ("Investment", [
        "vanguard", "fidelity", "schwab", "robinhood", "etf", "index fund",
        "mutual fund", "stock", "brokerage", "ira", "401k", "roth",
        "crypto", "bitcoin", "ethereum", "coinbase", "binance",
        "securities", "equity", "bond",
    ]),
    # Gaming & Entertainment Technology — MUST come before generic "computer"
    ("Technology & Gaming", [
        "gaming", "game", "razer", "corsair", "logitech", "asus rog",
        "msi gaming", "alienware", "steelseries", "nvidia gpu", "rtx",
        "gtx", "rx 580", "rx 6", "vega", "amd gpu",
        "gaming pc", "gaming desktop", "gaming laptop", "gaming chair",
        "gaming keyboard", "gaming mouse", "gaming monitor",
        "playstation", "xbox", "nintendo", "steam", "epic games",
        "graphics card", "gpu", "mechanical keyboard", "rgb",
    ]),
    # Technology (non-gaming)
    ("Technology", [
        "apple", "iphone", "macbook", "ipad", "samsung", "dell", "hp",
        "lenovo", "microsoft", "laptop", "desktop computer", "pc tower",
        "thin client", "optiplex", "thinkpad", "computer", "monitor",
        "printer", "scanner", "hard drive", "ssd", "ram", "cpu",
        "processor", "motherboard", "software", "adobe", "microsoft 365",
        "antivirus", "cloud storage",
    ]),
    # Food & Dining
    ("Food", [
        "starbucks", "mcdonald", "subway", "pizza", "restaurant",
        "dining", "cafe", "coffee", "doordash", "uber eats", "grubhub",
        "instacart", "whole foods", "trader joe", "grocery", "supermarket",
        "food", "bakery", "sushi", "burger", "taco",
    ]),
    # Subscriptions & Streaming
    ("Subscriptions", [
        "netflix", "spotify", "hulu", "disney+", "amazon prime",
        "youtube premium", "apple music", "hbo", "paramount",
        "subscription", "monthly plan", "annual plan",
    ]),
    # Shopping / Discretionary
    ("Discretionary", [
        "amazon", "ebay", "etsy", "walmart", "target", "best buy",
        "costco", "ikea", "zara", "h&m", "nike", "adidas",
        "shopping", "retail", "purchase", "order", "merchandise",
    ]),
    # Healthcare
    ("Healthcare", [
        "pharmacy", "cvs", "walgreens", "hospital", "clinic", "doctor",
        "dental", "vision", "medical", "health insurance", "rx",
        "prescription", "urgent care",
    ]),
    # Transport
    ("Transport", [
        "uber", "lyft", "taxi", "bus", "metro", "transit", "fuel",
        "petrol", "gas station", "shell", "bp", "exxon", "chevron",
        "parking", "toll", "car insurance", "vehicle", "auto",
    ]),
    # Essential Living (housing, utilities)
    ("Essential Living", [
        "rent", "mortgage", "electricity", "water bill", "utility",
        "internet", "phone bill", "insurance", "maintenance",
        "property tax", "homeowner", "hoa",
    ]),
    # ── Indian-specific categories ──────────────────────────────────────────
    ("Food & Dining", [
        "swiggy", "zomato", "blinkit", "bigbasket", "dunzo", "zepto",
        "grofers", "instamart", "kirana", "haldiram", "domino",
    ]),
    ("Investment", [
        "zerodha", "groww", "etmoney", "et money", "paytm money",
        "sip", "mutual fund", "ppf", "nps", "elss", "nsc",
        "lic premium", "fd maturity", "rd ", "recurring deposit",
    ]),
    ("Transport", [
        "ola", "rapido", "irctc", "redbus", "makemytrip", "cleartrip",
        "auto rickshaw", "metro card", "fastag", "yulu",
    ]),
    ("Shopping", [
        "flipkart", "meesho", "myntra", "ajio", "nykaa", "snapdeal",
        "jiomart", "tata cliq", "reliance smart",
    ]),
    ("Telecom", [
        "jio recharge", "airtel recharge", "bsnl", "vi recharge",
        "vodafone", "idea recharge", "mobile recharge",
    ]),
    ("Utilities", [
        "bescom", "msedcl", "tneb", "bwssb", "mtnl", "cesc",
        "electricity board", "water board", "piped gas", "mahanagar gas",
        "indraprastha gas",
    ]),
    ("Education", [
        "byju", "unacademy", "vedantu", "coursera", "udemy",
        "school fee", "college fee", "tuition", "exam fee",
    ]),
    ("EMI", [
        "emi", "loan emi", "home loan emi", "car loan", "personal loan",
        "bnpl", "bajaj finserv", "hdfc emi", "icici emi",
    ]),
]


def detect_currency(transactions: list) -> str:
    """Detect INR vs USD based on description signals."""
    if not transactions:
        return "USD"
    indian_signals = sum(
        1 for t in transactions
        if any(kw in str(t.get("description", "")).lower() for kw in [
            "upi", "neft", "imps", "₹", "inr", "rs.", "paytm", "phonepe",
            "gpay", "swiggy", "zomato", "flipkart", "jio", "airtel",
            "zerodha", "groww", "irctc", "bescom", "msedcl",
        ])
    )
    return "INR" if indian_signals >= max(1, len(transactions) * 0.2) else "USD"


def categorise_description(description: str) -> str:
    """Map a transaction/item description to a financial category."""
    desc_lower = description.lower()
    for category, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in desc_lower:
                return category
    return "Other"


# ─────────────────────────────────────────────────────────────────────────────
# OCR EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────

def _ocr_image(file_bytes: bytes) -> str:
    """Run Tesseract OCR on an image and return raw text."""
    if pytesseract is None or PILImage is None:
        return ""
    try:
        img = PILImage.open(io.BytesIO(file_bytes))
        # Upscale small images for better OCR accuracy
        w, h = img.size
        if w < 1200:
            scale = 1200 / w
            img = img.resize((int(w * scale), int(h * scale)), PILImage.LANCZOS)
        return pytesseract.image_to_string(img)
    except Exception as e:
        print(f"[OCR] Tesseract error: {e}")
        return ""


def _ocr_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF."""
    if PyPDF2 is None:
        return ""
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        return "\n".join(
            page.extract_text() or "" for page in reader.pages
        )
    except Exception as e:
        print(f"[OCR] PDF error: {e}")
        return ""


def _ocr_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file."""
    if docx is None:
        return ""
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)
    except Exception as e:
        print(f"[OCR] DOCX error: {e}")
        return ""


def _llm_parse_invoice(raw_text: str) -> list[dict]:
    """
    Use Nemotron to extract structured line-items from raw OCR invoice text.
    Returns a list of {date, description, amount, category} dicts.
    """
    from langchain_core.messages import SystemMessage, HumanMessage
    from agents.llm import llm as _llm

    system = """You are a financial data extraction engine. Given raw OCR text from an invoice or receipt, extract ALL line items.

Return ONLY a valid JSON array. Each element must have:
- "description": item name (string)
- "amount": total cost as a NEGATIVE float (it's an expense) — use gross/total price per line
- "date": invoice date if found, else "unknown"
- "category": one of [Income, Investment, Technology & Gaming, Technology, Food, Subscriptions, Discretionary, Healthcare, Transport, Essential Living, Other]

Rules:
- Gaming PCs, GPUs, gaming peripherals → "Technology & Gaming"  
- Generic computers, laptops, monitors → "Technology"
- DO NOT use "Essential Living" for electronics or computers
- Use negative amounts for all expenses
- If it is a payment received → positive amount → "Income"
- ALWAYS set category — never use null
- Return ONLY the JSON array. No explanation, no markdown fences."""

    human = f"Extract line items from this invoice/receipt text:\n\n{raw_text[:3000]}"

    try:
        response = _llm.invoke([
            SystemMessage(content=system),
            HumanMessage(content=human),
        ])
        raw = response.content.strip()
        # Strip <think>...</think> reasoning blocks from Nemotron
        raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
        # Strip markdown fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        # Extract JSON array if surrounded by extra text
        arr_match = re.search(r"\[.*\]", raw, re.DOTALL)
        if arr_match:
            raw = arr_match.group()
        items = json.loads(raw)
        if isinstance(items, list) and items:
            # Fix any null categories immediately
            for item in items:
                if not item.get("category"):
                    item["category"] = categorise_description(item.get("description", ""))
            print(f"[LLM Parse] Extracted {len(items)} line items from invoice")
            return items
        print("[LLM Parse] LLM returned empty list")
    except Exception as e:
        print(f"[LLM Parse] Failed ({type(e).__name__}: {e}), falling back to heuristic parser")

    return []


def _heuristic_parse_invoice(raw_text: str) -> list[dict]:
    """
    Regex-based fallback: extract price patterns and descriptions from OCR text.
    Handles formats like: "Description    Qty    Price    Total"
    """
    transactions = []
    lines = raw_text.split("\n")

    # Try to find invoice date
    date = "unknown"
    date_match = re.search(
        r"(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\w+ \d{1,2},?\s*\d{4})",
        raw_text
    )
    if date_match:
        date = date_match.group(1)

    # Look for lines with a currency amount at the end
    amount_pattern = re.compile(
        r"^(.{5,60?}?)\s+\$?\s*([\d,]+\.?\d{0,2})\s*$"
    )
    seen = set()
    for line in lines:
        line = line.strip()
        if len(line) < 8:
            continue
        m = amount_pattern.match(line)
        if m:
            desc = m.group(1).strip()
            raw_amt = m.group(2).replace(",", "")
            try:
                amount = float(raw_amt)
            except ValueError:
                continue
            # Skip header/summary rows
            if any(skip in desc.lower() for skip in [
                "total", "subtotal", "vat", "tax", "net worth", "gross",
                "description", "qty", "price", "amount", "no.", "item"
            ]):
                continue
            if desc in seen or amount == 0:
                continue
            seen.add(desc)
            category = categorise_description(desc)
            transactions.append({
                "date":        date,
                "description": desc,
                "amount":      -round(amount, 2),  # expense = negative
                "category":    category,
            })

    return transactions


# ─────────────────────────────────────────────────────────────────────────────
# MAIN EXTRACTION ROUTER
# ─────────────────────────────────────────────────────────────────────────────

def run_vision_extraction(file_bytes: bytearray, filename: str) -> list:
    """
    Routes to the correct extraction strategy based on file type.
    1. CSV  → pandas parse (categories re-validated)
    2. Image/PDF → Tesseract OCR → LLM structured parse → heuristic fallback
    """
    fname = filename.lower()
    raw_bytes = bytes(file_bytes)

    # ── CSV ──────────────────────────────────────────────────────────────────
    if fname.endswith(".csv"):
        try:
            df = pd.read_csv(io.BytesIO(raw_bytes))
            df.columns = [c.strip().lower() for c in df.columns]
            records = []
            for _, row in df.iterrows():
                desc = str(row.get("description", row.get("desc", row.get("name", ""))))
                # Re-categorise using smart engine if category is missing or suspicious
                raw_cat = str(row.get("category", "")).strip()
                if not raw_cat or raw_cat.lower() in ("other", "nan", ""):
                    category = categorise_description(desc)
                else:
                    # Validate: if desc looks like gaming but CSV says Essential Living, override
                    llm_cat = categorise_description(desc)
                    category = llm_cat if llm_cat != "Other" else raw_cat
                records.append({
                    "date":        str(row.get("date", "")),
                    "description": desc,
                    "amount":      float(row.get("amount", 0)),
                    "category":    category,
                })
            print(f"[Extract] CSV parsed: {len(records)} rows")
            return records
        except Exception as e:
            print(f"[Extract] CSV parse failed: {e}")

    # ── IMAGE (PNG / JPEG / WEBP) ─────────────────────────────────────────────
    is_image = any(fname.endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".webp"))
    is_pdf   = fname.endswith(".pdf")

    if is_image:
        print("[Extract] Running Tesseract OCR on image...")
        raw_text = _ocr_image(raw_bytes)
    elif is_pdf:
        print("[Extract] Extracting text from PDF...")
        raw_text = _ocr_pdf(raw_bytes)
    else:
        raw_text = _ocr_image(raw_bytes)

    print(f"[Extract] OCR text length: {len(raw_text)} chars")
    if raw_text:
        print(f"[Extract] OCR preview: {raw_text[:120].strip()}")

    if len(raw_text) < 20:
        print("[Extract] OCR returned too little text — using default mock")
        return _default_mock()

    # Try LLM-powered structured parse first
    print("[Extract] Sending OCR text to Nemotron for structured parsing...")
    items = _llm_parse_invoice(raw_text)

    # If LLM fails or returns nothing, fall back to heuristic
    if not items:
        print("[Extract] LLM parse returned empty — using heuristic invoice parser")
        items = _heuristic_parse_invoice(raw_text)

    # Final smart category correction pass — fix nulls and wrong categories
    for item in items:
        desc     = item.get("description", "")
        detected = categorise_description(desc)
        # Always override null/missing; also override "Essential Living" if
        # our keyword engine finds a more specific match
        current = item.get("category") or ""
        if not current or current == "Other" or (
            current == "Essential Living" and detected not in ("Other", "Essential Living")
        ):
            item["category"] = detected if detected != "Other" else (current or "Other")

    if not items:
        print("[Extract] No items extracted — using default mock")
        return _default_mock()

    print(f"[Extract] Final: {len(items)} line items — categories: {list(set(i['category'] for i in items))}")
    return items


def _default_mock() -> list:
    """Last-resort mock when all extraction paths fail."""
    return [
        {"date": "2026-07-01", "description": "Unknown Income",     "amount":  4200.00, "category": "Income"},
        {"date": "2026-07-02", "description": "Unknown Expense",    "amount": -1500.00, "category": "Other"},
    ]


# ─────────────────────────────────────────────────────────────────────────────
# ANALYTICS BUILDER
# ─────────────────────────────────────────────────────────────────────────────

def build_analytics(transactions: list) -> dict:
    """Derive the analytics bundle that the frontend dashboard renders."""
    if not transactions:
        return {}

    df = pd.DataFrame(transactions)
    categories = df.groupby("category")["amount"].sum().to_dict()

    income   = sum(v for v in categories.values() if v > 0)
    expenses = sum(abs(v) for v in categories.values() if v < 0)
    savings  = income - expenses
    sav_rate = (savings / income * 100) if income > 0 else 0
    score    = min(100, max(0, int(40 + sav_rate * 1.2)))

    # Anomaly detection: items > 2× their category mean
    anomalies = []
    for cat in df["category"].unique():
        subset = df[df["category"] == cat]
        if len(subset) < 2:
            continue
        mean_abs = subset["amount"].abs().mean()
        spikes = subset[subset["amount"].abs() > mean_abs * 2]
        for _, r in spikes.iterrows():
            anomalies.append(
                f"${abs(r['amount']):.0f} — \"{r['description']}\" is "
                f"{abs(r['amount'])/mean_abs:.1f}× above the {cat} baseline"
            )

    projections = []
    if savings > 0:
        projections.append(
            f"At current savings rate (${savings:.0f}/period), "
            f"you can accumulate $10,000 in ~{round(10000/savings,1)} periods."
        )
    if income > 0 and sav_rate >= 20:
        projections.append(
            f"Savings rate of {sav_rate:.1f}% is on track. "
            f"At 7% annual return, ${savings:.0f}/month becomes "
            f"${savings*12*17.5:,.0f} in 10 years."
        )

    return {
        "categories":   {k: round(v, 2) for k, v in categories.items()},
        "health_score": score,
        "anomalies":    anomalies,
        "projections":  projections,
        "currency":     detect_currency(transactions),
    }


# ─────────────────────────────────────────────────────────────────────────────
# FASTAPI ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    await initialize_db()


@app.get("/")
def read_root():
    return {"status": "ok"}


# ── UPI SMS helpers ────────────────────────────────────────────────────────────
_SMS_PATTERNS = [
    # HDFC: Rs.500.00 debited from a/c **1234 to SWIGGY on 10-07-26
    re.compile(r"[Rr]s\.?\s*(\d[\d,]*\.?\d*)\s+debited.*?to\s+([A-Z][A-Za-z0-9 @&_\-\.]+?)\s+(?:on|at)\s+([\d\-/]+)", re.IGNORECASE),
    # SBI: Your A/C X1234 debited by Rs 1500 on 10/07/26 trf to ZOMATO
    re.compile(r"debited by [Rr]s\.?\s*(\d[\d,]*\.?\d*).*?(?:trf to|to)\s+([A-Z][A-Za-z0-9 @&_\-\.]+?)(?:\s|$)", re.IGNORECASE),
    # ICICI: INR 250.00 debited from your ICICI Bank Account for purchase at AMAZON
    re.compile(r"INR\s+(\d[\d,]*\.?\d*)\s+debited.*?(?:at|to)\s+([A-Z][A-Za-z0-9 @&_\-\.]+?)(?:\s|$)", re.IGNORECASE),
    # Generic credit: Rs 5000 credited to your account from EMPLOYER
    re.compile(r"[Rr]s\.?\s*(\d[\d,]*\.?\d*)\s+credited.*?from\s+([A-Z][A-Za-z0-9 @&_\-\.]+?)(?:\s|$)", re.IGNORECASE),
    # UPI debit: Paid Rs.200 to merchant@upi
    re.compile(r"[Pp]aid\s+[Rr]s\.?\s*(\d[\d,]*\.?\d*)\s+to\s+([A-Za-z0-9@._\-]+)", re.IGNORECASE),
]

def parse_upi_sms(messages: list[str]) -> list[dict]:
    """Extract transactions from a list of Indian bank/UPI SMS strings."""
    transactions = []
    seen = set()
    for msg in messages:
        msg = msg.strip()
        if not msg:
            continue
        is_credit = any(w in msg.lower() for w in ["credited", "received", "credit"])
        for pattern in _SMS_PATTERNS:
            m = pattern.search(msg)
            if m:
                raw_amt = m.group(1).replace(",", "")
                merchant = m.group(2).strip().rstrip(".")
                try:
                    amount = float(raw_amt)
                except ValueError:
                    continue
                key = f"{merchant}:{amount}"
                if key in seen:
                    continue
                seen.add(key)
                category = categorise_description(merchant)
                transactions.append({
                    "date":        "unknown",
                    "description": merchant,
                    "amount":      amount if is_credit else -amount,
                    "category":    category if category != "Other" else ("Income" if is_credit else "Other"),
                    "source":      "upi_sms",
                })
                break
    return transactions


@app.post("/api/v1/extract/upload")
@limiter.limit("20/minute")
async def upload_document(
    request:         Request,
    file:            UploadFile = File(...),
    user_preference: str        = Form("buffett"),
    session_id:      str        = Form(None),
):
    raw_content = await file.read()

    if len(raw_content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds 20 MB limit.")

    if magic:
        detected = magic.from_buffer(raw_content[:2048], mime=True)
        is_csv_by_name = (file.filename or "").lower().endswith(".csv")
        if detected not in ALLOWED_MIME_TYPES and not is_csv_by_name:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported file type: {detected}. Accepted: PNG, JPEG, WEBP, PDF, CSV."
            )

    file_buffer = bytearray(raw_content)
    filename    = file.filename or "upload"

    try:
        structured_json  = run_vision_extraction(file_buffer, filename)
        analytics_bundle = build_analytics(structured_json)
        if not session_id:
            session_id = str(uuid.uuid4())

        # Zero-Trust wipe
        if len(file_buffer) > 0:
            char_arr = (ctypes.c_char * len(file_buffer)).from_buffer(file_buffer)
            ctypes.memset(ctypes.addressof(char_arr), 0, len(file_buffer))
        del file_buffer, raw_content
        gc.collect()

        print(f"[Upload] Persona={user_preference} | Session={session_id} | Txns={len(structured_json)}")
        print(f"[Upload] Categories: {list(analytics_bundle.get('categories', {}).keys())}")

        knowledge_context = _KNOWLEDGE_STORE.get(session_id, "")

        async with get_postgres_checkpointer() as cp:
            result = await orchestrator_graph.ainvoke(
                {
                    "user_preference": user_preference,
                    "transactions":    structured_json,
                    "revision_count":  0,
                    "currency":        analytics_bundle.get("currency", "USD"),
                    "knowledge_context": knowledge_context,
                },
                config={"configurable": {"thread_id": session_id}, "checkpointer": cp},
            )

        return {
            "status":          "success",
            "message":         "File ingested securely.",
            "persona_routed":  user_preference,
            "session_id":      session_id,
            "advisory_report": result.get("advisory_report", ""),
            "analytics":       analytics_bundle,
        }

    except Exception as e:
        import traceback
        print(f"[Upload Error] {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Shared pipeline helper ────────────────────────────────────────────────────
def _auto_select_persona(analytics: dict, requested: str) -> str:
    """Pick best guru persona from analytics data."""
    if requested not in ("buffett", "fire", "kiyosaki", "sethi", "indian_expert"):
        requested = "buffett"
    # If currency is INR and user hasn't forced a persona, prefer indian_expert
    if analytics.get("currency") == "INR" and requested == "buffett":
        return "indian_expert"
    cats    = analytics.get("categories", {})
    income  = sum(v for v in cats.values() if v > 0) or 1
    invest  = abs(cats.get("Investment", 0))
    health  = analytics.get("health_score", 50)
    savings_rate = (income - sum(abs(v) for v in cats.values() if v < 0)) / income * 100
    if savings_rate >= 30 or invest / income >= 0.15:
        return "buffett"
    if savings_rate <= 15:
        return "fire"
    if savings_rate >= 20:
        return "sethi"
    return "kiyosaki"


@app.post("/api/v1/extract/sms")
@limiter.limit("20/minute")
async def extract_sms(
    request: Request,
    data: dict,
):
    """
    Parse UPI/bank SMS messages and run the full advisory pipeline.
    Body: {"messages": ["sms text 1", "sms text 2", ...], "user_preference": "buffett"}
    """
    messages: list[str] = data.get("messages", [])
    user_preference: str = data.get("user_preference", "buffett")
    session_id: str = data.get("session_id", "")

    if not messages:
        raise HTTPException(status_code=400, detail="No messages provided.")

    structured_json = parse_upi_sms(messages)
    if not structured_json:
        raise HTTPException(status_code=422, detail="Could not extract any transactions from the provided messages.")

    analytics_bundle = build_analytics(structured_json)
    if not session_id:
        session_id = str(uuid.uuid4())
    persona          = _auto_select_persona(analytics_bundle, user_preference)

    print(f"[SMS] Parsed {len(structured_json)} txns | Persona={persona} | Session={session_id}")

    knowledge_context = _KNOWLEDGE_STORE.get(session_id, "")

    try:
        async with get_postgres_checkpointer() as cp:
            result = await orchestrator_graph.ainvoke(
                {
                    "user_preference": persona,
                    "transactions":    structured_json,
                    "revision_count":  0,
                    "currency":        analytics_bundle.get("currency", "INR"),
                    "knowledge_context": knowledge_context,
                },
                config={"configurable": {"thread_id": session_id}, "checkpointer": cp},
            )
        return {
            "status":          "success",
            "message":         f"Parsed {len(structured_json)} transactions from SMS.",
            "persona_routed":  persona,
            "session_id":      session_id,
            "advisory_report": result.get("advisory_report", ""),
            "analytics":       analytics_bundle,
            "sources_used":    ["upi_sms"],
        }
    except Exception as e:
        import traceback
        print(f"[SMS Error] {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# GOALS ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

# In-memory goal store (keyed by session_id)
# In production this would use the goals PostgreSQL table
_GOAL_STORE: dict[str, list[dict]] = {}


def _compute_goal_status(goal: dict, monthly_savings: float) -> dict:
    target   = goal["target_amount"]
    months   = goal["deadline_months"]
    currency = goal.get("currency", "USD")
    needed   = target / months if months > 0 else target
    income   = monthly_savings / 0.3 if monthly_savings > 0 else 1  # rough income estimate

    if monthly_savings <= 0:
        status = "off_track"
        proj   = 9999
    elif monthly_savings >= needed:
        status = "on_track"
        proj   = round(target / monthly_savings, 1)
    elif monthly_savings >= needed * 0.7:
        status = "at_risk"
        proj   = round(target / monthly_savings, 1)
    else:
        status = "off_track"
        proj   = round(target / monthly_savings, 1) if monthly_savings > 0 else 9999

    return {
        **goal,
        "monthly_required":              round(needed, 2),
        "projected_completion_months":   min(proj, 9999),
        "status":                        status,
        "pct_of_income_required":        round((needed / income * 100), 1) if income > 0 else 0,
    }


@app.post("/api/v1/goals")
async def create_goal(request: Request, data: dict):
    """
    Create a financial goal.
    Body: {session_id, name, target_amount, currency, deadline_months, priority}
    """
    session_id = data.get("session_id", "default")
    goal = {
        "id":               str(uuid.uuid4()),
        "name":             data.get("name", "Unnamed Goal"),
        "target_amount":    float(data.get("target_amount", 0)),
        "currency":         data.get("currency", "USD"),
        "deadline_months":  int(data.get("deadline_months", 6)),
        "priority":         data.get("priority", "medium"),
    }
    _GOAL_STORE.setdefault(session_id, []).append(goal)
    return _compute_goal_status(goal, monthly_savings=0)


@app.get("/api/v1/goals/{session_id}")
async def get_goals(session_id: str):
    """Return all goals for a session with computed status."""
    return [_compute_goal_status(g, 0) for g in _GOAL_STORE.get(session_id, [])]


@app.delete("/api/v1/goals/{goal_id}")
async def delete_goal(goal_id: str):
    """Delete a goal by ID."""
    for session_goals in _GOAL_STORE.values():
        original = len(session_goals)
        session_goals[:] = [g for g in session_goals if g["id"] != goal_id]
        if len(session_goals) < original:
            return {"deleted": True}
    raise HTTPException(status_code=404, detail="Goal not found.")


# ─────────────────────────────────────────────────────────────────────────────
# BUDGET ENVELOPE ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

_BUDGET_STORE: dict[str, dict[str, float]] = {}


def _build_budget_status(session_id: str, transactions: list) -> list[dict]:
    envelopes = _BUDGET_STORE.get(session_id, {})
    if not envelopes or not transactions:
        return []
    df = pd.DataFrame(transactions)
    spent_map = df[df["amount"] < 0].groupby("category")["amount"].sum().abs().to_dict()
    result = []
    for cat, limit in envelopes.items():
        spent = spent_map.get(cat, 0)
        pct   = (spent / limit * 100) if limit > 0 else 0
        result.append({
            "category":  cat,
            "allocated": round(limit, 2),
            "spent":     round(spent, 2),
            "remaining": round(max(0, limit - spent), 2),
            "pct_used":  round(pct, 1),
            "status":    "over" if pct > 100 else "warning" if pct > 80 else "ok",
        })
    return result


@app.post("/api/v1/budget/envelopes")
async def set_budget_envelopes(request: Request, data: dict):
    """
    Set budget envelopes for a session.
    Body: {session_id, envelopes: {category: monthly_limit}}
    """
    session_id = data.get("session_id", "default")
    envelopes  = data.get("envelopes", {})
    _BUDGET_STORE[session_id] = {k: float(v) for k, v in envelopes.items()}
    return [{"category": k, "allocated": float(v), "spent": 0, "remaining": float(v),
             "pct_used": 0, "status": "ok"} for k, v in envelopes.items()]


@app.get("/api/v1/budget/suggest")
async def suggest_budget(income: float, currency: str = "USD"):
    """
    Suggest 50/30/20 budget envelopes based on income.
    50% needs, 30% wants, 20% savings/investments.
    """
    if income <= 0:
        raise HTTPException(status_code=400, detail="Income must be > 0")

    if currency == "INR":
        return {
            "Essential Living": round(income * 0.40, 0),   # rent + utilities
            "Food & Dining":    round(income * 0.10, 0),
            "Transport":        round(income * 0.05, 0),
            "Investment":       round(income * 0.20, 0),   # SIP + savings
            "Discretionary":    round(income * 0.10, 0),
            "Telecom":          round(income * 0.03, 0),
            "Healthcare":       round(income * 0.05, 0),
            "Education":        round(income * 0.07, 0),
        }
    return {
        "Essential Living": round(income * 0.35, 0),
        "Food":             round(income * 0.10, 0),
        "Transport":        round(income * 0.05, 0),
        "Investment":       round(income * 0.20, 0),
        "Discretionary":    round(income * 0.15, 0),
        "Subscriptions":    round(income * 0.05, 0),
        "Healthcare":       round(income * 0.05, 0),
        "Savings Buffer":   round(income * 0.05, 0),
    }


# ─────────────────────────────────────────────────────────────────────────────
# SPLITWISE ENDPOINT (stub — replace with real Splitwise API client)
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/v1/splitwise/sync")
@limiter.limit("10/minute")
async def splitwise_sync(request: Request, data: dict):
    """
    Sync expenses from Splitwise.
    Body: {api_key, days_back, user_preference}
    Requires: pip install splitwise
    """
    api_key         = data.get("api_key", "")
    days_back       = int(data.get("days_back", 30))
    user_preference = data.get("user_preference", "sethi")
    session_id      = data.get("session_id", "")

    if not api_key:
        raise HTTPException(status_code=400, detail="Splitwise API key required.")

    try:
        from splitwise import Splitwise
        from datetime import datetime, timedelta

        sw      = Splitwise("", "", api_key=api_key)
        cutoff  = datetime.now() - timedelta(days=days_back)
        current_user = sw.getCurrentUser()
        expenses_raw = sw.getExpenses(dated_after=cutoff.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                       limit=200)

        transactions = []
        for exp in expenses_raw:
            if exp.deleted_at or not exp.cost:
                continue
            # Find user's net share
            for user in (exp.users or []):
                if str(user.id) == str(current_user.id):
                    owed = float(user.owed_share or 0)
                    if owed > 0:
                        transactions.append({
                            "date":        exp.date[:10] if exp.date else "unknown",
                            "description": exp.description or "Splitwise expense",
                            "amount":      -round(owed, 2),
                            "category":    categorise_description(exp.description or ""),
                            "source":      "splitwise",
                        })
                    break

    except ImportError:
        raise HTTPException(
            status_code=501,
            detail="Splitwise library not installed. Run: pip install splitwise"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Splitwise error: {str(e)}")

    if not transactions:
        raise HTTPException(status_code=422, detail="No expenses found in Splitwise for the given period.")

    analytics_bundle = build_analytics(transactions)
    if not session_id:
        session_id = str(uuid.uuid4())
    persona          = _auto_select_persona(analytics_bundle, user_preference)

    knowledge_context = _KNOWLEDGE_STORE.get(session_id, "")

    try:
        async with get_postgres_checkpointer() as cp:
            result = await orchestrator_graph.ainvoke(
                {"user_preference": persona, "transactions": transactions,
                 "revision_count": 0, "currency": analytics_bundle.get("currency", "USD"), "knowledge_context": knowledge_context},
                config={"configurable": {"thread_id": session_id}, "checkpointer": cp},
            )
        return {
            "status":          "success",
            "message":         f"Synced {len(transactions)} expenses from Splitwise.",
            "persona_routed":  persona,
            "session_id":      session_id,
            "advisory_report": result.get("advisory_report", ""),
            "analytics":       analytics_bundle,
            "sources_used":    ["splitwise"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─────────────────────────────────────────────────────────────────────────────
# KNOWLEDGE BASE ENDPOINT
# ─────────────────────────────────────────────────────────────────────────────

_KNOWLEDGE_STORE: dict[str, str] = {}

def _summarize_knowledge(raw_text: str) -> str:
    """Use the LLM to extract core financial principles from a book or article."""
    from langchain_core.messages import SystemMessage, HumanMessage
    from agents.llm import llm as _llm
    
    system = "You are a financial analyst. Extract the top 3-5 core personal finance principles from this text. Be concise, actionable, and focus purely on the financial philosophy."
    human = f"Extract principles from this excerpt:\n\n{raw_text[:8000]}"
    try:
        response = _llm.invoke([SystemMessage(content=system), HumanMessage(content=human)])
        raw = response.content.strip()
        raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
        return raw
    except Exception as e:
        print(f"[Knowledge] LLM error: {e}")
        return "Could not extract principles. Please rely on default guru personas."

@app.post("/api/v1/knowledge/upload")
@limiter.limit("5/minute")
async def upload_knowledge(
    request: Request,
    file: UploadFile = File(...),
    session_id: str = Form("default"),
):
    """
    Extract text from a financial book/article (PDF/DOCX) and store its philosophy.
    """
    raw_content = await file.read()
    if len(raw_content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds limit.")

    fname = (file.filename or "").lower()
    if fname.endswith(".pdf"):
        raw_text = _ocr_pdf(raw_content)
    elif fname.endswith(".docx"):
        raw_text = _ocr_docx(raw_content)
    else:
        raise HTTPException(status_code=415, detail="Knowledge base only supports PDF and DOCX.")
    
    if len(raw_text) < 50:
        raise HTTPException(status_code=422, detail="Not enough text extracted.")
        
    principles = _summarize_knowledge(raw_text)
    _KNOWLEDGE_STORE[session_id] = principles
    
    return {
        "status": "success",
        "message": f"Extracted philosophy from {file.filename}.",
        "principles": principles,
        "session_id": session_id
    }

