from __future__ import annotations

import json
from pathlib import Path
import pandas as pd

from src.recurring import detect_recurring

BASE = Path(__file__).resolve().parent
DATA = BASE / "data" / "synthetic_transactions.csv"
OUT = BASE / "index.html"

df = pd.read_csv(DATA, parse_dates=["date"])
preds = detect_recurring(df)

payload = {}
for cid in sorted(df["customer_id"].unique()):
    c_tx = df[df.customer_id.eq(cid)].copy()
    c_pred = preds[preds.customer_id.eq(cid)].copy()
    recurring_merchants = set(c_pred.merchant.tolist()) if not c_pred.empty else set()
    hist = c_tx[c_tx.merchant.isin(recurring_merchants)][["date", "merchant", "amount"]].copy()
    hist["date"] = hist["date"].dt.strftime("%Y-%m-%d")
    pred_rows = c_pred.to_dict(orient="records") if not c_pred.empty else []
    payload[cid] = {
        "predictions": pred_rows,
        "history": hist.to_dict(orient="records"),
    }

html = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Upcoming Commitments</title>
<style>
:root { --bg:#f6f7f9; --card:#ffffff; --text:#172033; --muted:#667085; --line:#e4e7ec; --accent:#155eef; --warn:#b54708; }
*{box-sizing:border-box} body{margin:0;font-family:Inter,Arial,sans-serif;background:var(--bg);color:var(--text)}
.wrap{max-width:1100px;margin:32px auto;padding:0 20px}.top{display:flex;align-items:flex-end;justify-content:space-between;gap:20px;flex-wrap:wrap}
h1{margin:0;font-size:30px}.sub{color:var(--muted);margin-top:6px}.controls{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
label{font-size:12px;color:var(--muted);display:flex;flex-direction:column;gap:4px} select,input{padding:9px 10px;border:1px solid var(--line);border-radius:8px;background:white;min-width:140px}
.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:22px 0}.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;box-shadow:0 1px 2px rgba(16,24,40,.04)}
.metric .label{font-size:12px;color:var(--muted)}.metric .value{font-size:25px;font-weight:700;margin-top:4px}.warning{display:none;border-left:4px solid #f79009;background:#fffaeb;padding:12px 14px;border-radius:8px;margin-bottom:18px;color:var(--warn)}
.grid{display:grid;grid-template-columns:1.4fr 1fr;gap:16px}.section-title{font-weight:700;margin-bottom:10px}.table{width:100%;border-collapse:collapse;font-size:14px}.table th,.table td{padding:10px 8px;border-bottom:1px solid var(--line);text-align:left}.table th{font-size:12px;color:var(--muted)}
.badge{display:inline-block;padding:3px 8px;border-radius:999px;background:#eef4ff;color:#3538cd;font-size:12px}.payment{padding:11px;border:1px solid var(--line);border-radius:10px;margin-bottom:8px;cursor:pointer}.payment:hover{border-color:#84adff}.payment.active{border-color:var(--accent);background:#eff4ff}.amount{float:right;font-weight:700}.muted{color:var(--muted);font-size:13px}.btns{display:flex;gap:8px;margin-top:14px}.btn{border:0;border-radius:8px;padding:9px 12px;cursor:pointer;background:#eef2f6;color:#344054}.btn.primary{background:var(--accent);color:white}.feedback{font-size:13px;margin-top:10px;color:#027a48}.foot{color:var(--muted);font-size:12px;margin-top:18px}.bar{height:8px;background:#eaecf0;border-radius:99px;overflow:hidden;margin-top:5px}.bar>span{display:block;height:100%;background:#84adff}
@media(max-width:800px){.metrics,.grid{grid-template-columns:1fr}}
</style>
</head>
<body><div class="wrap">
<div class="top"><div><h1>Upcoming Commitments</h1><div class="sub">Digital-banking product · synthetic data</div></div>
<div class="controls"><label>Synthetic customer<select id="customer"></select></label><label>Current balance (£)<input id="balance" type="number" value="1750" min="0" step="50"></label><label>Alert threshold (£)<input id="threshold" type="number" value="500" min="0" step="50"></label></div></div>
<div class="metrics"><div class="card metric"><div class="label">Current balance</div><div class="value" id="mBalance"></div></div><div class="card metric"><div class="label">Expected commitments</div><div class="value" id="mCommit"></div></div><div class="card metric"><div class="label">Projected available</div><div class="value" id="mProjected"></div></div></div>
<div class="warning" id="warning">Projected available balance may fall below your chosen alert threshold.</div>
<div class="grid"><div class="card"><div class="section-title">Upcoming recurring commitments</div><table class="table"><thead><tr><th>Merchant</th><th>Next date</th><th>Expected</th><th>Confidence</th></tr></thead><tbody id="upcoming"></tbody></table></div>
<div class="card"><div class="section-title">Review a detected recurring payment</div><div id="payments"></div><div id="detail" class="muted">Select a payment to review its prediction and history.</div></div></div>
<div class="foot">Scope: recurring-payment detection, projected-balance calculation, review/correction interaction and supporting product artefacts. Uses synthetic data only; no real bank or customer data is used.</div>
</div>
<script>
const DATA = __PAYLOAD__;
const customerSel=document.getElementById('customer'); Object.keys(DATA).forEach(c=>{const o=document.createElement('option');o.value=c;o.textContent=c;customerSel.appendChild(o)});
const fmt=n=>'£'+Number(n).toLocaleString('en-GB',{minimumFractionDigits:2,maximumFractionDigits:2});
const state={selected:null,feedback:{}};
function render(){const cid=customerSel.value;const bal=Number(document.getElementById('balance').value||0);const threshold=Number(document.getElementById('threshold').value||0);const p=DATA[cid].predictions;
const latestDates=p.map(x=>new Date(x.last_payment_date));const latest=latestDates.length?new Date(Math.max(...latestDates)):new Date('2026-06-30');const asOf=new Date(latest);asOf.setDate(asOf.getDate()+1);const end=new Date(asOf);end.setDate(end.getDate()+35);
const upcoming=p.filter(x=>{const d=new Date(x.predicted_next_date);return d>=asOf&&d<=end}).sort((a,b)=>new Date(a.predicted_next_date)-new Date(b.predicted_next_date));
const committed=upcoming.reduce((s,x)=>s+Number(x.expected_amount),0), projected=bal-committed;document.getElementById('mBalance').textContent=fmt(bal);document.getElementById('mCommit').textContent=fmt(committed);document.getElementById('mProjected').textContent=fmt(projected);document.getElementById('warning').style.display=projected<threshold?'block':'none';
const tb=document.getElementById('upcoming');tb.innerHTML=upcoming.length?upcoming.map(x=>`<tr><td>${x.merchant}<div class="muted">${x.category}</div></td><td>${x.predicted_next_date}</td><td>${fmt(x.expected_amount)}</td><td><span class="badge">${Math.round(x.confidence*100)}%</span></td></tr>`).join(''):'<tr><td colspan="4" class="muted">No predicted commitments in the next 35 days.</td></tr>';
const box=document.getElementById('payments');box.innerHTML=p.map(x=>`<div class="payment ${state.selected===x.merchant?'active':''}" data-m="${x.merchant}"><span class="amount">${fmt(x.expected_amount)}</span><b>${x.merchant}</b><div class="muted">${x.predicted_next_date} · ${Math.round(x.confidence*100)}% confidence</div></div>`).join('');box.querySelectorAll('.payment').forEach(el=>el.onclick=()=>{state.selected=el.dataset.m;renderDetail(cid);render()});
if(state.selected&&!p.some(x=>x.merchant===state.selected))state.selected=null;if(state.selected)renderDetail(cid);
}
function renderDetail(cid){const p=DATA[cid].predictions.find(x=>x.merchant===state.selected);if(!p)return;const h=DATA[cid].history.filter(x=>x.merchant===state.selected);const max=Math.max(...h.map(x=>Number(x.amount)));const hist=h.map(x=>`<div style="margin:7px 0"><div class="muted">${x.date} · ${fmt(x.amount)}</div><div class="bar"><span style="width:${Math.max(8,Number(x.amount)/max*100)}%"></span></div></div>`).join('');const f=state.feedback[cid+'|'+p.merchant];document.getElementById('detail').innerHTML=`<div><b>${p.merchant}</b><div class="muted">Expected ${fmt(p.expected_amount)} on ${p.predicted_next_date}</div>${hist}<div class="btns"><button class="btn primary" onclick="saveFeedback('${cid}','${p.merchant}','Confirmed')">Confirm</button><button class="btn" onclick="saveFeedback('${cid}','${p.merchant}','Not recurring')">Not recurring</button></div>${f?`<div class="feedback">Review saved in-session: ${f}</div>`:''}</div>`}
function saveFeedback(cid,m,v){state.feedback[cid+'|'+m]=v;renderDetail(cid)}
[customerSel,document.getElementById('balance'),document.getElementById('threshold')].forEach(el=>el.addEventListener('input',render));customerSel.value='C0001';render();
</script></body></html>'''
OUT.write_text(html.replace('__PAYLOAD__', json.dumps(payload, default=str)), encoding='utf-8')
print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes)")
