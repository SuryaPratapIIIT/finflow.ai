import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.research_agent import research
from agents.finance_agent import assess
from data.db import get_overdue_invoices

def test_pipeline():
    print("Fetching an overdue invoice from the DB...")
    invoices = get_overdue_invoices()
    if not invoices:
        print("No overdue invoices found in the database.")
        return
        
    # Take the first overdue invoice
    target_invoice = invoices[0]
    invoice_id = target_invoice['id']
    
    print(f"\n--- Running Research Agent for Invoice ID: {invoice_id} ---")
    research_data = research(invoice_id)
    
    print("\n[Research Data Output]")
    print(json.dumps(research_data, indent=2))
    
    print("\n--- Running Finance Agent ---")
    print("Calling Groq LLM (Ensure GROQ_API_KEY is set in .env)...")
    
    assessment = assess(research_data)
    
    print("\n[Assessment Output]")
    print(json.dumps(assessment, indent=2))

if __name__ == "__main__":
    test_pipeline()
