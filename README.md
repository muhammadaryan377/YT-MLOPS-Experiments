# Distributor AI MVP 🇵🇰

A small **Vertical AI + Agentic AI** prototype for Pakistani FMCG distributors and wholesalers.

The MVP takes a WhatsApp-style Roman Urdu / English customer message and converts it into a structured order decision:

```text
WhatsApp-style message
        ↓
Normalize text
        ↓
Extract products + quantities
        ↓
Match distributor SKUs
        ↓
Check current stock
        ↓
Check outstanding balance + credit limit
        ↓
Agent decides next action
        ↓
Draft reply for customer
```

## Example

Input:

```text
10 carton Pepsi 500 ml, 5 Dew aur 2 carton Sting bhej dena.
pichla balance bhi check kar lena
```

The seeded demo customer (`Ali General Store`) has an existing balance and a small credit limit. The agent therefore detects both:

- Sting stock shortage
- credit-limit violation
- balance inquiry
- minimum payment required before order release

## Run locally

### 1. Clone and switch to the MVP branch

```bash
git clone https://github.com/muhammadaryan377/YT-MLOPS-Experiments.git
cd YT-MLOPS-Experiments
git checkout distributor-ai-mvp
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the API

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

Interactive API docs:

```text
http://127.0.0.1:8000/docs
```

## Run tests

```bash
pytest -q
```

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Browser demo UI |
| GET | `/health` | Health check |
| GET | `/v1/catalog` | Seed product catalog |
| GET | `/v1/customers/{customer_id}` | Customer balance/credit info |
| POST | `/v1/messages/process` | Run the distributor agent |

## Current MVP boundaries

This first version intentionally **does not send real WhatsApp messages or change inventory automatically**. It prepares a decision and suggested reply first. That human-in-the-loop design prevents costly actions while the extraction accuracy is still being validated.

The current parser is deterministic so the project runs with **zero API keys and zero LLM cost**. The next phase can add Ollama/Groq for stronger Roman Urdu understanding while preserving deterministic SKU, stock, pricing and credit checks.

## Next milestones

1. PostgreSQL product/customer/order database
2. real WhatsApp Cloud API webhook
3. Ollama/Groq structured order extraction
4. fuzzy SKU/catalog retrieval for thousands of products
5. order confirmation + inventory reservation
6. payment promises and recovery agent
7. voice-note transcription (Urdu/Roman Urdu)
8. distributor dashboard
9. salesman/route agent
10. demand forecasting and stock-out prediction

## Why this is agentic

The model is not supposed to directly decide business truth. The workflow separates capabilities:

```text
understand → match → check stock → check credit → decide → communicate
```

This structure can later be represented as LangGraph nodes with persistence, retries, interrupts and human approvals.
