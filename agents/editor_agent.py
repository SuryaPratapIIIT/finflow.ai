import os
import sys
import json
import yaml
from groq import Groq

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_reflection_review(draft, research_data):
    # Lazy import to avoid circular dependency
    from agents.reflection_agent import review
    return review(draft, research_data)

PROMPT_EMAIL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "editor_agent_email_v1.yaml")
PROMPT_VOICE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "editor_agent_voice_v1.yaml")

def load_prompt(path):
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return data["system_prompt"]

def generate_text(system_prompt: str, user_prompt: str) -> str:
    api_key = os.environ.get("GROQ_API_KEY", "your_groq_api_key_here")
    client = Groq(api_key=api_key)
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

def _draft_single(prompt_path, research_data, assessment, issues=None) -> str:
    system_prompt = load_prompt(prompt_path)
    
    user_prompt = f"Research Data:\n{json.dumps(research_data, indent=2)}\n\n"
    user_prompt += f"Finance Assessment:\n{json.dumps(assessment, indent=2)}\n\n"
    
    if issues:
        user_prompt += f"PREVIOUS ISSUES TO FIX (Retry Mode):\n"
        for issue in issues:
            user_prompt += f"- {issue}\n"
            
    user_prompt += "\nPlease draft the message now."
    return generate_text(system_prompt, user_prompt)

def draft(research_data: dict, assessment: dict) -> dict:
    """
    Drafts email and voice scripts. Loops up to 1 time with Reflection Agent if needs_retry is True.
    Returns the final versions.
    """
    email_draft = _draft_single(PROMPT_EMAIL_PATH, research_data, assessment)
    voice_draft = _draft_single(PROMPT_VOICE_PATH, research_data, assessment)
    
    result = {
        "email_version": email_draft,
        "voice_script_version": voice_draft,
        "email_reflection": {},
        "voice_reflection": {}
    }
    
    # Review Email
    email_review = get_reflection_review(email_draft, research_data)
    result["email_reflection"] = email_review
    if email_review.get("needs_retry", False):
        print("Email draft needs retry based on reflection. Retrying...")
        issues = email_review.get("issues", [])
        email_draft = _draft_single(PROMPT_EMAIL_PATH, research_data, assessment, issues)
        result["email_version"] = email_draft
        # Re-review capped at 1 retry
        result["email_reflection"] = get_reflection_review(email_draft, research_data)
        
    # Review Voice
    voice_review = get_reflection_review(voice_draft, research_data)
    result["voice_reflection"] = voice_review
    if voice_review.get("needs_retry", False):
        print("Voice script needs retry based on reflection. Retrying...")
        issues = voice_review.get("issues", [])
        voice_draft = _draft_single(PROMPT_VOICE_PATH, research_data, assessment, issues)
        result["voice_script_version"] = voice_draft
        # Re-review capped at 1 retry
        result["voice_reflection"] = get_reflection_review(voice_draft, research_data)
        
    return result
