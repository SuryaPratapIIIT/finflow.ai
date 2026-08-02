import argparse
import json
from orchestrator.graph import run_pipeline
from data.db import get_overdue_invoices

def main():
    parser = argparse.ArgumentParser(description="FinFlow AI Pipeline")
    parser.add_argument("--invoice-id", type=int, help="Run pipeline on a specific invoice ID")
    parser.add_argument("--test-batch", action="store_true", help="Run pipeline on 3 overdue invoices")
    
    args = parser.parse_args()
    
    if args.test_batch:
        invoices = get_overdue_invoices()
        if not invoices:
            print("No overdue invoices found.")
            return
            
        test_invoices = invoices[:3]
        for inv in test_invoices:
            inv_id = inv['id']
            print(f"\n{'='*50}\nProcessing Invoice ID: {inv_id}\n{'='*50}")
            result = run_pipeline(inv_id)
            print_result(result)
            
    elif args.invoice_id:
        print(f"Processing Invoice ID: {args.invoice_id}")
        result = run_pipeline(args.invoice_id)
        print_result(result)
    else:
        parser.print_help()

def print_result(result: dict):
    if "error" in result:
        print(f"PIPELINE ERROR: {result['error']}")
        return
        
    outputs = result.get("outputs", {})
    drafts = outputs.get("drafts", {})
    
    if "error" in drafts:
        print(f"DRAFT ERROR: {drafts['error']}")
        return
    
    print("\n--- FINAL EMAIL DRAFT ---")
    print(drafts.get("email_version", "N/A"))
    
    print("\n--- FINAL VOICE SCRIPT ---")
    print(drafts.get("voice_script_version", "N/A"))
    
    metrics = result.get("metrics", {})
    print("\n--- METRICS ---")
    print(json.dumps(metrics, indent=2))
    print("\nCheck the 'logs/' folder for the full execution trace.")

if __name__ == "__main__":
    main()
