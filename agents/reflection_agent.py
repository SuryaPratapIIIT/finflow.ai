import os
import sys
import json
import yaml
from groq import Groq

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PROMPT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "reflection_agent_v1.yaml")

def load_prompt():
    with open(PROMPT_PATH, "r") as f:
        data = yaml.safe_load(f)
    return data["system_prompt"]

def review(draft: str, research_data: dict) -> dict:
    """
    Reviews a draft against policy chunks for factual consistency and tone.
    Returns dict with {"groundedness_score": int, "tone_score": int, "issues": list, "needs_retry": bool}
    """
    api_key = os.environ.get("GROQ_API_KEY", "your_groq_api_key_here")
    client = Groq(api_key=api_key)
    
    system_prompt = load_prompt()
    user_prompt = f"Research Data (Contains Policies):\n{json.dumps(research_data, indent=2)}\n\n"
    user_prompt += f"Draft to Review:\n{draft}\n\nReview this draft according to your instructions and output JSON."
    
    max_retries = 1
    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile", # Reflection requires better reasoning
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0
            )
            
            raw_text = response.choices[0].message.content.strip()
            
            # Clean markdown code fences if present
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
                
            parsed = json.loads(raw_text.strip())
            
            # Enforce needs_retry logic just in case the LLM got it wrong
            if parsed.get("groundedness_score", 5) < 3 or parsed.get("tone_score", 5) < 3:
                parsed["needs_retry"] = True
                
            return parsed
            
        except json.JSONDecodeError as e:
            if attempt < max_retries:
                continue
            else:
                return {
                    "groundedness_score": 1,
                    "tone_score": 1,
                    "issues": [f"Failed to parse JSON from Reflection LLM: {e}"],
                    "needs_retry": True
                }
        except Exception as e:
            return {
                "groundedness_score": 1,
                "tone_score": 1,
                "issues": [f"Error calling LLM: {str(e)}"],
                "needs_retry": True
            }
