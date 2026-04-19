import re

def analyze_heuristics(text: str):
    """
    Analyzes text and extracts lightweight heuristic rules for a cybersecurity dashboard.
    Returns a dictionary with triggered rules and mocked realistic email flags.
    """
    text_lower = text.lower()
    
    # 1. Rule Engine heuristics
    triggered_rules = []
    
    # Check for suspicious links
    if re.search(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", text):
        triggered_rules.append({"rule": "Contains Links", "severity": "Medium", "desc": "Message contains hyperlinked URLs."})
        
    # Check for urgency language
    urgent_words = ['urgent', 'immediate', 'action required', 'act now', 'suspended', 'verify', 'password', 'alert']
    if any(word in text_lower for word in urgent_words):
        triggered_rules.append({"rule": "Urgent Language", "severity": "High", "desc": "Common phishing pressure words detected."})
        
    # Check for monetary requests
    money_words = ['$', 'cash', 'prize', 'winner', 'lottery', 'wire transfer', 'crypto', 'bitcoin', 'btc']
    if any(word in text_lower for word in money_words):
        triggered_rules.append({"rule": "Financial Motivation", "severity": "High", "desc": "Text implies financial transactions or rewards."})

    # Check for strange formatting (e.g. excessive capitalization)
    words = text.split()
    caps_word_count = sum(1 for w in words if w.isupper() and len(w) > 2)
    if len(words) > 0 and (caps_word_count / len(words)) > 0.3:
        triggered_rules.append({"rule": "Abnormal Formatting", "severity": "Low", "desc": "Excessive use of capital letters."})

    # 2. Mock realistic security flags (SPF/DKIM/DMARC) - simulated based on text context
    # If text has high heuristic triggers, let's simulate a failure in security headers.
    security_flags = {
        "SPF": {"status": "PASS", "color": "green", "desc": "Sender IP authorized"},
        "DKIM": {"status": "PASS", "color": "green", "desc": "Signature valid"},
        "DMARC": {"status": "PASS", "color": "green", "desc": "Policy strictly aligned"}
    }
    
    if len(triggered_rules) >= 2:
        security_flags["DKIM"] = {"status": "FAIL", "color": "red", "desc": "Signature invalid or missing"}
        if "Financial Motivation" in [r["rule"] for r in triggered_rules]:
             security_flags["DMARC"] = {"status": "FAIL", "color": "red", "desc": "Policy violation (reject)"}
             security_flags["SPF"] = {"status": "SOFTFAIL", "color": "orange", "desc": "IP not explicitly permitted"}
             
    return {
        "rules": triggered_rules,
        "flags": security_flags
    }
