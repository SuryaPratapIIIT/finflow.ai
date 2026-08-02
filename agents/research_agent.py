import os
import sys

# Ensure imports work when run from tests or root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.db import get_connection, get_customer, get_payment_history
from rag.retriever import retrieve

def research(invoice_id: int) -> dict:
    """
    Pulls the invoice, the customer, their payment history, and 2-3 relevant 
    policy chunks based on the invoice's overdue status.
    """
    conn = get_connection()
    invoice_row = conn.execute(
        "SELECT id, customer_id, amount, due_date, status, "
        "CAST(julianday('now') - julianday(due_date) AS INTEGER) AS days_overdue "
        "FROM invoices WHERE id = ?", (invoice_id,)
    ).fetchone()
    conn.close()
    
    if not invoice_row:
        return {"error": f"Invoice {invoice_id} not found."}
        
    invoice = dict(invoice_row)
    customer_id = invoice["customer_id"]
    
    customer = get_customer(customer_id)
    history = get_payment_history(customer_id)
    
    days_overdue = invoice.get("days_overdue", 0)
    query = f"customer is {max(0, days_overdue)} days late and overdue"
    
    policies = retrieve(query, k=3)
    
    return {
        "invoice": invoice,
        "customer": customer,
        "payment_history": history,
        "relevant_policies": policies
    }
