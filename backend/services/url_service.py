import os
import requests
import re
import pickle
import urllib.parse
import jellyfish
from typing import Tuple
from models.schemas import AnalyzeTextResponse, FlaggedPhrase
from dotenv import load_dotenv

load_dotenv()
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

# Suspicious URL indicators for rule-based detection
SUSPICIOUS_TLDS = [".xyz", ".top", ".loan", ".win", ".club", ".stream", ".gq", ".ml", ".cf", ".tk", ".ga", ".ru", ".cn"]
URL_SHORTENERS = ["bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "buff.ly", "adf.ly", "bit.do", "cutt.ly"]
DANGEROUS_KEYWORDS = ["login", "verify", "secure", "account", "update", "bank", "paypal", "admin", "free", "gift", "winner", "claim"]
PROTECTED_BRANDS = ["google", "paypal", "github", "microsoft", "apple", "amazon", "netflix"]

_local_url_model = None

def get_local_url_model():
    global _local_url_model
    if _local_url_model is not None: return _local_url_model
    model_path = os.path.join(os.path.dirname(__file__), "..", "ml", "url_threat_detector_final.pkl")
    if os.path.exists(model_path):
        try:
            with open(model_path, 'rb') as f:
                import joblib
                _local_url_model = joblib.load(f)
                return _local_url_model
        except: pass
    return None

def get_severity_from_score(score: int) -> str:
    if score <= 25: return "LOW"
    if score <= 50: return "MED"
    if score <= 75: return "HIGH"
    return "CRIT"

def parse_host_details(url: str) -> Tuple[str, str]:
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    parsed = urllib.parse.urlparse(url)
    hostname = parsed.netloc.lower()
    hostname = re.sub(r'^www\.', '', hostname)
    
    parts = hostname.split('.')
    primary_domain = parts[-2] if len(parts) >= 2 else parts[0]
    return hostname, primary_domain

def analyze_url(url: str) -> AnalyzeTextResponse:
    # URL extraction if text contains more than just the URL
    extracted_url = url
    url_match = re.search(r'(https?://[^\s]+)', url)
    if url_match:
        extracted_url = url_match.group(1)
        
    # ─── PRE-ML LAYER: WHITELIST & BRAND IMPERSONATION ───
    try:
        hostname, primary_domain = parse_host_details(extracted_url)
        
        # Layer 1: Exact Match Whitelist (Prevents False Positives)
        if primary_domain in PROTECTED_BRANDS:
            return AnalyzeTextResponse(
                threat_score=0,
                severity="LOW",
                verdict="SAFE",
                confidence=1.0,
                flagged_phrases=[],
                recommended_action="URL appears safe. Verified official domain.",
                engine_source="Rule-Based Whitelist"
            )

        # Layer 2: Typosquatting & Subdomain Spoofing
        for brand in PROTECTED_BRANDS:
            dist = jellyfish.levenshtein_distance(primary_domain, brand)
            if 0 < dist <= 2:
                return AnalyzeTextResponse(
                    threat_score=100,
                    severity="CRIT",
                    verdict="MALICIOUS",
                    confidence=1.0,
                    flagged_phrases=[FlaggedPhrase(text=primary_domain, reason=f"Typosquatting Attack (Spoofing '{brand}')", level="red")],
                    recommended_action="DO NOT CLICK. High-confidence brand spoofing detected.",
                    engine_source="Rule-Based Typosquatting Engine"
                )
                
            if brand in hostname and primary_domain != brand:
                return AnalyzeTextResponse(
                    threat_score=95,
                    severity="CRIT",
                    verdict="MALICIOUS",
                    confidence=0.99,
                    flagged_phrases=[FlaggedPhrase(text=hostname, reason=f"Brand Impersonation Subdomain (Spoofing '{brand}')", level="red")],
                    recommended_action="DO NOT CLICK. Deceptive subdomain routing detected.",
                    engine_source="Rule-Based Heuristics"
                )
    except Exception as e:
        print(f"Hybrid preprocessing error: {e}")

    API_URL = "https://api-inference.huggingface.co/models/elftsdmr/malware-url-detect"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"} if HF_API_TOKEN else {}
    
    fallback_used = False
    score = 0
    confidence = 0.0
    engine_source = ""
    
    # ─── PRIMARY: LOCAL ML MODEL ───
    local_model = get_local_url_model()
    local_prob = None
    if local_model:
        try:
            local_prob = local_model.predict_proba([extracted_url])[0][1]
            score = int(local_prob * 100)
            confidence = max(local_prob, 1.0 - local_prob)
            engine_source = "Local ML Model"
        except: pass
        
    # ─── SECONDARY: HUGGINGFACE API ───
    if local_prob is None:
        if HF_API_TOKEN:
            try:
                response = requests.post(API_URL, headers=headers, json={"inputs": extracted_url}, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and isinstance(result[0], list):
                        res = result[0]
                    elif isinstance(result, list) and isinstance(result[0], dict):
                        res = result
                    else:
                        fallback_used = True
                        res = []
                    
                    if not fallback_used and res:
                        malicious_score = next((item['score'] for item in res if item['label'].upper() in ['MALICIOUS', 'LABEL_1', '1', 'PHISHING', 'MALWARE', 'DEFACEMENT']), 0.0)
                        confidence = max(item['score'] for item in res)
                        score = int(malicious_score * 100)
                        engine_source = "HuggingFace URL Model"
                else:
                    fallback_used = True
            except Exception as e:
                print(f"HF URL API Error: {e}")
                fallback_used = True
        else:
            fallback_used = True
            
    flagged = []
    
    # ─── FALLBACK & HEURISTICS: RULE-BASED URL ANALYSIS ───
    if fallback_used:
        print("Using rule-based URL detection fallback.")
        url_lower = extracted_url.lower()
        
        # Check TLDs
        if any(tld in url_lower for tld in SUSPICIOUS_TLDS):
            score += 40
            flagged.append(FlaggedPhrase(text=extracted_url, reason="Suspicious Top-Level Domain (TLD) associated with spam/malware.", level="red"))
            
        # Check Shorteners
        if any(shortener in url_lower for shortener in URL_SHORTENERS):
            score += 30
            flagged.append(FlaggedPhrase(text=extracted_url, reason="URL Shortener hides the actual destination.", level="amber"))
            
        # Check IP-based URLs
        if re.search(r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url_lower):
            score += 50
            flagged.append(FlaggedPhrase(text=extracted_url, reason="Direct IP address in URL instead of domain name.", level="red"))
            
        # Check multiple subdomains / long URLs
        if len(url_lower) > 75 or url_lower.count('.') > 3:
            score += 20
            flagged.append(FlaggedPhrase(text=extracted_url, reason="Unusually long URL or excessive subdomains (obfuscation attempt).", level="amber"))
            
        # Check dangerous keywords in path/subdomain
        for kw in DANGEROUS_KEYWORDS:
            if kw in url_lower:
                score += 15
                flagged.append(FlaggedPhrase(text=kw, reason="High-risk keyword found in URL path or subdomain.", level="amber"))
                
        score = min(score, 100)
        confidence = 0.85
        
    severity = get_severity_from_score(score)
    verdict = "MALICIOUS" if score > 50 else "SAFE"
    
    # Ensure flagged phrases exist if verdict is malicious via ML
    if not fallback_used and score > 50 and not flagged:
         flagged.append(FlaggedPhrase(text=extracted_url[:30]+"...", reason=f"{engine_source} detected structural similarities to known malicious domains.", level="red"))
         
    if verdict == "MALICIOUS":
        action = "DO NOT CLICK. Block this domain in your firewall/proxy. Do not enter credentials or download files."
    else:
        action = "URL appears safe, but always verify the domain matches the expected brand name before entering credentials."

    return AnalyzeTextResponse(
        threat_score=score,
        severity=severity,
        verdict=verdict,
        confidence=confidence,
        flagged_phrases=flagged[:5], # Keep it concise
        recommended_action=action,
        engine_source=engine_source if not fallback_used else "Local Rule Engine"
    )