import os
import sys
import sqlite3
import glob
import json
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.graph import run_pipeline

class InvoiceCreate(BaseModel):
    customer_id: int
    amount: float
    due_date: str
    status: str = 'overdue'

app = FastAPI(title="FinFlow AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'finflow.db')
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/api/metrics/dso")
def get_dso_trend():
    conn = get_db_connection()
    query = '''
        SELECT 
            strftime('%Y-%m', i.due_date) as month,
            AVG(p.days_late) as avg_days_late
        FROM invoices i
        JOIN payment_history p ON i.id = p.invoice_id
        GROUP BY month
        ORDER BY month;
    '''
    try:
        df = pd.read_sql_query(query, conn)
        return {"data": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/metrics/top-overdue")
def get_top_overdue():
    conn = get_db_connection()
    query = '''
        SELECT 
            c.name,
            SUM(i.amount) as total_overdue
        FROM invoices i
        JOIN customers c ON i.customer_id = c.id
        WHERE i.status = 'overdue'
        GROUP BY c.id, c.name
        ORDER BY total_overdue DESC
        LIMIT 5;
    '''
    try:
        df = pd.read_sql_query(query, conn)
        return {"data": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/logs")
def get_agent_logs():
    logs = []
    log_files = glob.glob(os.path.join(LOGS_DIR, "run_*.json"))
    for file in log_files:
        try:
            with open(file, 'r') as f:
                data = json.load(f)
                
                invoice_id = data.get('invoice_id')
                outputs = data.get('outputs', {})
                assessment = outputs.get('assessment', {})
                drafts = outputs.get('drafts', {})
                
                tone = assessment.get('tone', 'unknown') if isinstance(assessment, dict) else 'unknown'
                email = drafts.get('email_version', 'N/A') if isinstance(drafts, dict) else 'N/A'
                
                metrics = data.get('metrics', {})
                score = metrics.get('final_email_groundedness', 'N/A')
                
                logs.append({
                    "id": invoice_id,
                    "filename": os.path.basename(file),
                    "tone": tone.capitalize() if isinstance(tone, str) else str(tone),
                    "score": score,
                    "draft": email
                })
        except Exception:
            continue
    return {"data": logs}

@app.get("/api/customers")
def get_customers():
    conn = get_db_connection()
    try:
        df = pd.read_sql_query("SELECT id, name FROM customers ORDER BY name", conn)
        return {"data": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/api/invoices")
def create_invoice(invoice: InvoiceCreate):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO invoices (customer_id, amount, due_date, status) VALUES (?, ?, ?, ?)",
            (invoice.customer_id, invoice.amount, invoice.due_date, invoice.status)
        )
        conn.commit()
        return {"message": "Invoice created successfully", "id": cursor.lastrowid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/invoices/pending")
def get_pending_invoices():
    conn = get_db_connection()
    try:
        query = '''
            SELECT i.id, c.name, i.amount, i.due_date, 
                   CAST(julianday('now') - julianday(i.due_date) AS INTEGER) as days_overdue
            FROM invoices i
            JOIN customers c ON i.customer_id = c.id
            WHERE i.status = 'overdue'
            ORDER BY days_overdue DESC
            LIMIT 5;
        '''
        df = pd.read_sql_query(query, conn)
        return {"data": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/api/orchestrate/{invoice_id}")
def trigger_pipeline(invoice_id: int):
    try:
        result = run_pipeline(invoice_id)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class LogUpdate(BaseModel):
    draft: str

@app.put("/api/logs/{filename}")
def update_agent_log(filename: str, log_update: LogUpdate):
    log_file = os.path.join(LOGS_DIR, filename)
    if not os.path.exists(log_file):
        raise HTTPException(status_code=404, detail="Log not found")
    try:
        with open(log_file, 'r') as f:
            data = json.load(f)
        
        if 'outputs' not in data:
            data['outputs'] = {}
        if 'drafts' not in data['outputs']:
            data['outputs']['drafts'] = {}
        
        data['outputs']['drafts']['email_version'] = log_update.draft
        
        with open(log_file, 'w') as f:
            json.dump(data, f, indent=2)
            
        return {"message": "Log updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/logs/{filename}")
def delete_agent_log(filename: str):
    log_file = os.path.join(LOGS_DIR, filename)
    if not os.path.exists(log_file):
        raise HTTPException(status_code=404, detail="Log not found")
    try:
        os.remove(log_file)
        return {"message": "Log deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class PromptUpdate(BaseModel):
    content: str

@app.get("/api/prompts/{agent_type}")
def get_prompt(agent_type: str):
    prompt_file = os.path.join(PROMPTS_DIR, f"{agent_type}.yaml")
    if not os.path.exists(prompt_file):
        raise HTTPException(status_code=404, detail="Prompt not found")
    with open(prompt_file, 'r') as f:
        return {"content": f.read()}

@app.put("/api/prompts/{agent_type}")
def update_prompt(agent_type: str, prompt: PromptUpdate):
    prompt_file = os.path.join(PROMPTS_DIR, f"{agent_type}.yaml")
    if not os.path.exists(prompt_file):
        raise HTTPException(status_code=404, detail="Prompt not found")
    with open(prompt_file, 'w') as f:
        f.write(prompt.content)
    return {"message": "Prompt updated successfully"}
