# Equil - The Finance Wizard

Equil is a Smart Wealth Management Platform powered by a resilient, multi-agent NLP pipeline. It securely digests financial data, cross-examines it against multi-guru philosophical frameworks, and delivers highly personalized, educational financial analytics.

## Core Architectural Highlights

### 1. LangGraph Loop Engineering
The orchestration backend leverages LangGraph to create self-correcting, fault-tolerant execution loops:
- **OCR Fallback Loop**: The `Extraction Agent` features a rigorous validation node that checks the structural integrity of extracted JSON data. If the primary Google Vision OCR fails or returns malformed data, a conditional edge automatically loops the state back, increments the retry counter, and dynamically triggers the secondary local Tesseract OCR.
- **Advisory Critique Loop**: The `Advisory Agent` generates draft recommendations which are immediately routed to a `Critique Node`. If the output violates safety constraints (e.g., direct stock-picking advice), it is intercepted, flagged with a `SAFETY VIOLATION`, and looped back for forced revision, ensuring strictly educational guidance.

### 2. Zero-Trust Memory Management
Financial security is the absolute priority. The data ingestion endpoint (`/api/v1/extract/upload`) strictly enforces a Zero-Trust policy:
- Uploaded bank statements and screenshots are held **strictly in-memory** via buffered byte arrays.
- Buffers are excluded from database state checkpointing.
- The pipeline utilizes explicit memory purging (`del` statements paired with `gc.collect()`) within a `finally` block to guarantee sensitive financial data is completely eradicated from RAM immediately upon processing completion. No raw financial data is ever written to disk or long-term storage.

### 3. Multi-Agent Orchestration Pipeline
- **Extraction Agent**: Ingests and structures raw documents (Images, CSVs) using multi-OCR strategies and Pandas.
- **Synthesis Agent**: Dynamically retrieves and chunks philosophical financial paradigms (Warren Buffett, Robert Kiyosaki, Ramit Sethi).
- **Analytics Agent**: Executes smart bucketing, anomaly detection, and 3-6 month cash flow projections.
- **Advisory Agent**: The core reasoning engine that cross-examines the structured spend data against the synthesis paradigms to generate a balanced, multi-perspective recommendation.

## Deployment Scaffolding

### Backend (Railway/Render)
The backend is fully containerized. A `Dockerfile` exposes the FastAPI service on port 8000 via Uvicorn.
To deploy manually on Railway:
```bash
railway up
```

### Frontend (Vercel)
The Next.js frontend is configured as plug-and-play for Vercel deployment.
To deploy via Vercel CLI:
```bash
vercel --prod
```
