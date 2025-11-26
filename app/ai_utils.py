import random

def check_image_quality(image_path):
    """
    Simulates checking for blur, glare, and resolution.
    Returns: quality_score (0-100), is_blurry (bool)
    """
    # In a real app, use cv2.Laplacian(img, cv2.CV_64F).var()
    score = random.randint(60, 99)
    return score, score < 50

def detect_forgery(image_path):
    """
    Simulates checking for Photoshop edits, edge manipulation, and MRZ mismatch.
    Returns: forgery_score (0-100), flags (list of issues)
    """
    issues = []
    score = random.randint(70, 100)
    
    if score < 80:
        issues.append("Suspicious Edges Detected")
    if score < 70:
        issues.append("Pixel Inconsistency")
        
    return score, issues

def check_liveness(selfie_path, cnic_path):
    """
    Simulates Face Matching and Liveness Detection.
    Returns: match_score (0-100), is_live (bool)
    """
    match_score = random.randint(75, 99)
    is_live = True # Assume live for demo unless we want to force fail
    
    return match_score, is_live

def extract_text_ocr(image_path):
    """
    Simulates OCR extraction.
    """
    return {
        "name": "Auto-Extracted Name",
        "cnic": "42101-1234567-1",
        "dob": "01-01-1990"
    }

def check_fraud_rules(customer_data):
    """
    Real-time deterministic fraud checks.
    Returns: fraud_score (0-100), alerts (list)
    """
    alerts = []
    score = 0
    
    # 1. Disposable Email Check
    disposable_domains = ["tempmail.com", "10minutemail.com", "guerrillamail.com", "mailinator.com"]
    email_domain = customer_data.get('email', '').split('@')[-1]
    
    if email_domain in disposable_domains:
        score += 40
        alerts.append(f"Disposable Email Detected ({email_domain})")
        
    # 2. Suspicious Income vs Age (Mock Logic)
    # In real app, calculate age from CNIC/DOB
    if customer_data.get('income_range') == "Above 200k" and random.choice([True, False]): 
        # Simulating a mismatch for demo purposes if we don't have real age
        pass 

    # 3. Duplicate Identity (Simulated for Demo)
    # In real app, query DB for fuzzy match
    if customer_data.get('phone', '').startswith("030000000"):
        score += 30
        alerts.append("Suspicious Phone Pattern")

    # 4. Velocity Check (Simulated)
    # If created_at is very recent
    
    return score, alerts

def simulate_ocr_extraction(file_path=None):
    """
    Simulates extracting details from a CNIC image.
    Returns: dict of extracted fields
    """
    if not file_path:
        return None
        
    # Simulate "Reading" delay or logic based on filename
    return {
        "name": "Asharib Khan",
        "cnic": "42101-9876543-1",
        "dob": "15-08-1995",
        "expiry": "15-08-2030"
    }
