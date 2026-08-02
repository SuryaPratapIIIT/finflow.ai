import os
import sys
import json
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.research_agent import research
from agents.finance_agent import assess
from agents.editor_agent import draft

LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")

# TRADEOFF EXPLANATION:
# LangGraph vs Plain Python Pipeline
# LangGraph is excellent for complex, cyclical multi-agent workflows (e.g., letting agents dynamically converse 
# back and forth or managing complex state branching). However, in this specific architecture, the workflow is 
# strictly linear at the macro level (Research -> Finance -> Editor). The only cyclical part is the reflection 
# retry loop, which we already elegantly encapsulated entirely within the `editor_agent`'s `draft()` function.
# Therefore, introducing LangGraph here would add unnecessary dependency weight and cognitive overhead for a 
# simple linear DAG. A plain Python pipeline is easier to debug, faster, and perfectly sufficient for this flow.

def run_pipeline(invoice_id: int) -> dict:
    start_time = time.time()
    
    # 1. Research Agent
    research_data = research(invoice_id)
    if "error" in research_data:
        return {"error": research_data["error"]}
        
    # 2. Finance Agent
    assessment = assess(research_data)
    
    # 3. Editor Agent (includes internal Reflection loop)
    # We only draft if assessment didn't fail
    if "error" in assessment:
        drafts = {"error": f"Assessment failed: {assessment['error']}"}
    else:
        drafts = draft(research_data, assessment)
        
    end_time = time.time()
    
    # Check if a retry happened (if needs_retry was True in the initial reflection)
    email_retry = drafts.get("email_reflection", {}).get("needs_retry", False) if isinstance(drafts, dict) else False
    voice_retry = drafts.get("voice_reflection", {}).get("needs_retry", False) if isinstance(drafts, dict) else False
    
    run_log = {
        "timestamp": datetime.now().isoformat(),
        "invoice_id": invoice_id,
        "latency_seconds": round(end_time - start_time, 2),
        "prompt_versions": {
            "finance": "finance_agent_v1.yaml",
            "editor_email": "editor_agent_email_v1.yaml",
            "editor_voice": "editor_agent_voice_v1.yaml",
            "reflection": "reflection_agent_v1.yaml"
        },
        "outputs": {
            "research": research_data,
            "assessment": assessment,
            "drafts": drafts
        },
        "metrics": {
            "email_retry_happened": email_retry,
            "voice_retry_happened": voice_retry,
            "final_email_groundedness": drafts.get("email_reflection", {}).get("groundedness_score") if isinstance(drafts, dict) else None,
            "final_voice_groundedness": drafts.get("voice_reflection", {}).get("groundedness_score") if isinstance(drafts, dict) else None
        }
    }
    
    # Write to log file
    os.makedirs(LOGS_DIR, exist_ok=True)
    # Windows paths can't have colons, so format time with hyphens
    log_filename = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_inv{invoice_id}.json"
    log_path = os.path.join(LOGS_DIR, log_filename)
    
    with open(log_path, "w") as f:
        json.dump(run_log, f, indent=2)
        
    return run_log
