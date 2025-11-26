import random
from datetime import datetime
import difflib

def calculate_risk_profile(customer, documents=None, existing_customers=None, face_match_score=None):
    """
    Calculates the Risk Score (0-100), Trust Score (0-100), and Segment.
    """
    risk_score = 0
    trust_score = 50 # Start with neutral trust
    reasons = []
    
    # --- 1. Identity & Contact Analysis ---
    email = customer.get('email', '').lower()
    phone = customer.get('phone', '')
    cnic = customer.get('cnic', '')
    
    disposable_domains = ['tempmail.com', '10minutemail.com', 'throwawaymail.com', 'guerrillamail.com']
    
    if any(domain in email for domain in disposable_domains):
        risk_score += 40
        trust_score -= 30
        reasons.append("Disposable email domain detected")
    else:
        trust_score += 10 # Valid email provider

    if len(phone) < 10:
        risk_score += 10
        reasons.append("Invalid phone number format")
    else:
        trust_score += 5

    # --- 2. Address Analysis ---
    address = customer.get('address', '')
    if len(address) < 15:
        risk_score += 15
        trust_score -= 10
        reasons.append("Incomplete or short address")
    else:
        trust_score += 5

    # --- 3. CNIC Analysis ---
    # Simulate Expired CNIC check (Mock rule: if CNIC ends with '9', treat as expiring soon)
    if cnic.endswith('9'):
        risk_score += 25
        trust_score -= 15
        reasons.append("CNIC nearing expiry")
    
    # --- 4. Document Quality (Simulated) ---
    # In a real app, we'd use CV to detect blur.
    # Simulation: Random chance of "Blurry" if not provided
    is_blurry = False
    if random.random() < 0.05: # Reduced to 5% chance
        is_blurry = True
        risk_score += 30
        trust_score -= 20
        reasons.append("Uploaded document detected as blurry")

    # --- 5. Face Match Analysis (Simulated or Passed) ---
    if face_match_score is not None:
        if face_match_score < 70:
            risk_score += 40
            trust_score -= 30
            reasons.append(f"Low Face Match Score ({face_match_score}%)")
        else:
            trust_score += 10

    # --- 6. Duplicate Identity Check (Strict & Fuzzy) ---
    is_returning = False
    duplicate_found = False
    
    if existing_customers:
        current_name = customer.get('full_name', '').lower()
        
        for existing in existing_customers:
            # Strict Checks
            if existing.get('cnic') == cnic:
                risk_score = 100
                reasons.append(f"CRITICAL: Duplicate CNIC detected (User ID: {existing.get('id')})")
                duplicate_found = True
                break
            
            existing_email = existing.get('email', '').lower()
            if existing_email == email:
                risk_score += 50
                reasons.append(f"Duplicate Email detected (User ID: {existing.get('id')})")
                duplicate_found = True
            
            if existing.get('phone') == phone:
                risk_score += 40
                reasons.append(f"Duplicate Phone detected (User ID: {existing.get('id')})")
                duplicate_found = True
                
            # Fuzzy Name Match (Only if no strict match found yet)
            if not duplicate_found:
                existing_name = existing.get('full_name', '').lower()
                similarity = difflib.SequenceMatcher(None, current_name, existing_name).ratio()
                
                if similarity > 0.90: # Increased threshold to 90%
                    risk_score += 30
                    reasons.append(f"Potential duplicate name (Match: {existing_name}, Score: {int(similarity*100)}%)")
    
    # Simulate "Returning Customer" positive trait if no duplicate found but logic says so (legacy logic)
    if not reasons and not duplicate_found and random.random() < 0.2:
        is_returning = True
        trust_score += 20
        reasons.append("Returning customer detected (Positive)")

    # --- Final Calculation ---
    risk_score = min(max(risk_score, 0), 100)
    trust_score = min(max(trust_score, 0), 100)

    # --- Segmentation ---
    income_range = customer.get('income_range', '0-50k')
    segment = "Standard"
    
    if risk_score > 70:
        segment = "High Risk"
    elif "100k" in income_range or "High" in income_range:
        segment = "High Income"
    elif is_returning:
        segment = "Returning Customer"
    elif risk_score < 20:
        segment = "Low Risk / Prime"

    return {
        "risk_score": risk_score,
        "trust_score": trust_score,
        "risk_level": "High" if risk_score > 70 else "Medium" if risk_score > 30 else "Low",
        "segment": segment,
        "reasons": reasons
    }

def assess_loan_eligibility(risk_score, income_range):
    """
    Determines Loan Eligibility based on Risk Score and Income.
    
    ALL LOANS ARE SET TO PENDING - Admin must manually approve/reject.
    Risk score and max limit are calculated for admin reference only.
    """
    # All loans require manual admin approval
    status = "Pending"
    max_limit = 0
    
    # Base Limit based on Income (for admin reference)
    base_limit = 50000 # Default for Low Income
    if "50k-100k" in income_range:
        base_limit = 100000
    elif "100k" in income_range or "High" in income_range:
        base_limit = 250000
        
    # Calculate suggested limit based on risk (for admin reference only)
    if risk_score < 40:
        # Low risk - suggest full base limit
        max_limit = base_limit
    elif risk_score <= 70:
        # Medium risk - suggest 50% of base limit
        max_limit = int(base_limit * 0.5)
    else:
        # High risk - suggest rejection, but admin decides
        max_limit = 0

    return {
        "status": status,  # Always "Pending" - admin must manually approve/reject
        "max_limit": max_limit,  # Suggested limit for admin reference
        "currency": "PKR"
    }

def detect_forgery(file_path):
    """
    Simulates AI Document Forgery Detection.
    """
    # Simulation
    return {
        "is_forged": False,
        "confidence": 0.98,
        "reasons": []
    }
    if "fake" in file_path.lower() or random.random() < 0.05:
        is_forged = True
        reasons = ["Pixel manipulation detected", "Font inconsistency"]
        confidence = 0.88
    
    return {
        "is_forged": is_forged,
        "confidence": confidence,
        "reasons": reasons
    }

def check_liveness(selfie_path, cnic_path):
    """
    Simulates Liveness and Face Matching.
    Returns: { match_score: int, is_live: bool }
    """
    # Mock Simulation
    match_score = random.randint(85, 99)
    is_live = True
    
    if random.random() < 0.05:
        match_score = random.randint(20, 60)
        is_live = False
        
    return {
        "match_score": match_score,
        "is_live": is_live
    }
