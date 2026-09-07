import os
import requests
import json
from models.schemas import AnalyzeTextResponse, FlaggedPhrase
from dotenv import load_dotenv
import time

load_dotenv()

HF_API_TOKEN = os.getenv("HF_API_TOKEN")

PHISHING_KEYWORDS = ["verify", "suspend", "urgent", "click here", "confirm", "reward", "password", "paypal", "account", "24 hours"]
INJECTION_KEYWORDS = ["ignore previous", "you are now", "forget", "DAN", "jailbreak", "pretend", "override", "disregard", "act as", "new instructions"]

def get_severity_from_score(score: int) -> str:
    if score <= 25: return "LOW"
    if score <= 50: return "MED"
    if score <= 75: return "HIGH"
    return "CRIT"

def analyze_injection(text: str) -> AnalyzeTextResponse:
    # Reverted to the active deepset model
    API_URL = "https://router.huggingface.co/hf-inference/models/protectai/deberta-v3-base-prompt-injection-v2"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"} if HF_API_TOKEN else {}
    
    fallback_used = False
    score = 0
    confidence = 0.0
    
    if HF_API_TOKEN:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # 15-second timeout and retry loop to handle Hugging Face cold starts
                response = requests.post(API_URL, headers=headers, json={"inputs": text}, timeout=15)
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and isinstance(result[0], list):
                        res = result[0]
                    elif isinstance(result, list) and isinstance(result[0], dict):
                        res = result
                    else:
                        fallback_used = True
                        break
                    
                    # Extract the injection score
                    inj_score = next((item['score'] for item in res if item['label'].upper() in ['INJECTION', 'LABEL_1', '1', 'LABEL_1']), 0.0)
                    confidence = max(item['score'] for item in res)
                    score = int(inj_score * 100)
                    fallback_used = False
                    break  # Success, exit the retry loop
                    
                elif response.status_code == 503:
                    # Catch 503 errors (Model is loading on Hugging Face servers)
                    fallback_used = True
                    time.sleep(5)  # Wait 5 seconds and retry
                else:
                    fallback_used = True
                    break
            except Exception:
                fallback_used = True
                break
    else:
        fallback_used = True
        
    if fallback_used:
        print("HF API unavailable or token missing for Injection, using fallback scorer")
        matched = [kw for kw in INJECTION_KEYWORDS if kw in text.lower()]
        score = int((len(matched) / len(INJECTION_KEYWORDS)) * 100)
        confidence = 0.8
        
    severity = get_severity_from_score(score)
    verdict = "INJECTION" if score > 50 else "SAFE"
    
    flagged = []
    text_lower = text.lower()
    for kw in INJECTION_KEYWORDS:
        if kw in text_lower:
            lvl = "red" if kw in ["ignore previous", "jailbreak", "override"] else "amber"
            flagged.append(FlaggedPhrase(text=kw, reason=f"Common prompt injection trigger phrase.", level=lvl))
            
    if score > 50 and not flagged:
        flagged.append(FlaggedPhrase(text=text[:30]+"...", reason="Attempt to manipulate or bypass system instructions detected.", level="red"))
        
    action = "Block this input from being processed by the LLM. Log the user's IP." if verdict == "INJECTION" else "Input is safe to process."
    
    return AnalyzeTextResponse(
        threat_score=score,
        severity=severity,
        verdict=verdict,
        confidence=confidence,
        flagged_phrases=flagged,
        recommended_action=action
    )