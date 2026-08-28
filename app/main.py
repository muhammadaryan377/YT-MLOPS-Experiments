from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from app.agent import DistributorAgent
from app.schemas import MessageRequest, MessageResponse
from app.store import get_customer, list_products

app = FastAPI(
    title="Distributor AI MVP",
    version="0.1.0",
    description="Roman Urdu/English distributor order assistant for Pakistani wholesalers.",
)
agent = DistributorAgent()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "distributor-ai-mvp"}


@app.get("/v1/catalog")
def catalog():
    return list_products()


@app.get("/v1/customers/{customer_id}")
def customer(customer_id: str):
    item = get_customer(customer_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return item


@app.post("/v1/messages/process", response_model=MessageResponse)
def process_message(payload: MessageRequest) -> MessageResponse:
    try:
        return agent.process(payload.customer_id, payload.message)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/", response_class=HTMLResponse)
def demo() -> str:
    return r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Distributor AI MVP</title>
  <style>
    body{font-family:Inter,Arial,sans-serif;background:#111827;color:#f9fafb;margin:0;padding:40px}
    .wrap{max-width:900px;margin:auto}.card{background:#1f2937;border:1px solid #374151;border-radius:18px;padding:24px;margin-bottom:20px}
    textarea,select{width:100%;box-sizing:border-box;background:#111827;color:white;border:1px solid #4b5563;border-radius:10px;padding:12px;margin:8px 0 16px}
    button{background:#f59e0b;color:#111827;border:0;border-radius:10px;padding:12px 18px;font-weight:700;cursor:pointer}
    pre{white-space:pre-wrap;word-break:break-word;background:#0b1220;padding:16px;border-radius:12px;overflow:auto}.muted{color:#9ca3af}
  </style>
</head>
<body><div class="wrap">
  <h1>Distributor AI MVP</h1>
  <p class="muted">Roman Urdu / English WhatsApp-style order → stock + credit decision.</p>
  <div class="card">
    <label>Customer</label>
    <select id="customer"><option value="ali-general-store">Ali General Store</option><option value="city-mart">City Mart</option></select>
    <label>Message</label>
    <textarea id="message" rows="5">10 carton Pepsi 500 ml, 5 Dew aur 2 carton Sting bhej dena. pichla balance bhi check kar lena</textarea>
    <button onclick="runAgent()">Process message</button>
  </div>
  <div class="card"><h3>Agent response</h3><pre id="output">Click “Process message”.</pre></div>
</div>
<script>
async function runAgent(){
  const out=document.getElementById('output'); out.textContent='Processing...';
  const r=await fetch('/v1/messages/process',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({customer_id:document.getElementById('customer').value,message:document.getElementById('message').value})});
  const data=await r.json(); out.textContent=JSON.stringify(data,null,2);
}
</script></body></html>'''
