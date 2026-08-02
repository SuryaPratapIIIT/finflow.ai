import os
import sys
import json
import yaml
from groq import Groq

# Ensure imports work when run from tests or root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Simple parser for .env if python-dotenv is not installed
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        for line in f:
            if "=" in line and not line.strip().startswith("#"):
                key, val = line.strip().split("=", 1)
                os.environ[key] = val

PROMPT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "finance_agent_v1.yaml")

def load_prompt():
    with open(PROMPT_PATH, "r") as f:
        data = yaml.safe_load(f)
    return data["system_prompt"]

def assess(research_data: dict) -> dict:
    """
    Calls Groq to score urgency and recommend tone based on research data.
    Parses output with a try/except retry block for valid JSON.
    """
    api_key = os.environ.get("GROQ_API_KEY", "your_groq_api_key_here")
    client = Groq(api_key=api_key)
    
    system_prompt = load_prompt()
    user_prompt = f"Here is the research data:\n{json.dumps(research_data, indent=2)}\n\nAssess this data according to your instructions."
    
    max_retries = 1
    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0
            )
            
            raw_text = response.choices[0].message.content.strip()
            
            # Clean up markdown fences if the model ignores the instruction
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
                
            raw_text = raw_text.strip()
            
            parsed = json.loads(raw_text)
            return parsed
            
        except json.JSONDecodeError as e:
            if attempt < max_retries:
                print(f"Failed to parse JSON on attempt {attempt+1}, retrying... Error: {e}")
                continue
            else:
                return {"error": "Failed to parse JSON from LLM after retries.", "raw_output": raw_text}
        except Exception as e:
            return {"error": str(e)}
