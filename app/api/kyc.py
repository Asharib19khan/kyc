from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app import db, security_utils, models
import shutil
import os
from typing import Optional

router = APIRouter()

@router.post("/register")
def register_customer(
    full_name: str = Form(...),
    cnic: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    income_range: str = Form(...),
    password: str = Form(...),
    dob: Optional[str] = Form(None),  # Added DOB parameter (optional)
    father_name: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None)
):
    try:
        print(f"Registering user: {full_name}, {email}")
        
        # 1. Calculate Initial Risk Profile
        print("Calculating risk profile...")
        from app.services import risk_engine
        import random
        
        # Fetch existing customers for duplicate check
        conn = db.get_conn()
        conn.row_factory = db.sqlite3.Row
        cursor = conn.cursor()
        rows = cursor.execute("SELECT id, full_name, cnic, email, phone FROM Customers").fetchall()
        
        # Decrypt sensitive data for comparison
        existing_customers = []
        for row in rows:
            cust = dict(row)
            try:
                cust['cnic'] = security_utils.decrypt_data(cust['cnic'])
                cust['phone'] = security_utils.decrypt_data(cust['phone'])
            except Exception:
                pass
            existing_customers.append(cust)
            
        conn.close()
        
        cust_data = {
            "email": email,
            "address": address,
            "cnic": cnic,
            "phone": phone,
            "income_range": income_range,
            "full_name": full_name
        }
        
        # Simulate Face Match Score
        simulated_face_match = random.randint(60, 99)
        
        risk_profile = risk_engine.calculate_risk_profile(
            cust_data,
            existing_customers=existing_customers,
            face_match_score=simulated_face_match
        )
        print(f"Risk profile calculated: {risk_profile}")

        # 2. Hash Password
        from app import auth
        hashed_pw = auth.hash_password(password)

        # 3. Insert Customer
        print("Inserting customer into DB...")
        cust_id, customer_code = db.insert_customer(
            full_name, cnic, email, phone, address, income_range, hashed_pw,
            trust_score=risk_profile['trust_score'],
            segment=risk_profile['segment']
        )
        print(f"Customer inserted with ID: {cust_id}, Code: {customer_code}")
        
        # 4. Assess Loan Eligibility
        print("Assessing loan eligibility...")
        loan_eligibility = risk_engine.assess_loan_eligibility(risk_profile['risk_score'], income_range)
        db.save_loan_eligibility(
            cust_id,
            risk_profile['risk_score'],
            income_range,
            loan_eligibility['status'],
            loan_eligibility['max_limit']
        )
        
        # 5. Create Verification Record with AI Recommendations
        print("Creating verification record...")
        
        # Build AI analysis as recommendations (not auto-decisions)
        ai_recommendations = []
        
        # Critical risk alerts
        if risk_profile['risk_score'] > 70:
            ai_recommendations.append("⚠️ HIGH RISK: Risk score exceeds safety threshold (>70)")
        elif risk_profile['risk_score'] > 50:
            ai_recommendations.append("⚡ MODERATE RISK: Risk score elevated (>50)")
        
        # Trust score evaluation
        if risk_profile['trust_score'] < 50:
            ai_recommendations.append("🔍 LOW TRUST: Trust score below average (<50)")
        
        # Build final remarks with AI analysis
        base_analysis = f"AI Analysis: {', '.join(risk_profile['reasons'])}" if risk_profile['reasons'] else "Initial Registration"
        
        if ai_recommendations:
            auto_remarks = base_analysis + " | AI RECOMMENDATIONS: " + " • ".join(ai_recommendations)
        else:
            auto_remarks = base_analysis + " | ✅ AI Assessment: Normal risk profile"
            
        db.create_verification_record(
            cust_id,
            risk_score=risk_profile['risk_score'],
            trust_score=risk_profile['trust_score'],
            remarks=auto_remarks
        )
        
        print(f"Verification record created as PENDING (Risk: {risk_profile['risk_score']}, Trust: {risk_profile['trust_score']})")
        
        # 6. Generate Financials (Demo)
        print("Generating mock financials...")
        db.generate_mock_financials(cust_id)
        print("Mock financials generated.")
        
        if latitude and longitude:
            print(f"Customer {cust_id} Location: {latitude}, {longitude}")
            
        return {
            "status": "success",
            "customer_id": cust_id,
            "customer_code": customer_code,
            "message": f"Registration successful! Your unique customer code is: {customer_code}. Please save this code - you will need it to login."
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"CRITICAL ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.post("/upload/{customer_id}")
def upload_document(
    customer_id: int,
    doc_type: str = Form(...),
    file: UploadFile = File(...)
):
    print(f"Uploading file for customer {customer_id}: {doc_type}")
    os.makedirs("uploads", exist_ok=True)
    file_location = f"uploads/{customer_id}_{doc_type}_{file.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
        
    print(f"File saved at {file_location}")
    db.insert_document(customer_id, doc_type, file_location)
    print("Document record inserted into DB.")
    
    return {"status": "success", "file_path": file_location}

@router.post("/extract-cnic")
def extract_cnic_data(file: UploadFile = File(...)):
    os.makedirs("uploads", exist_ok=True)
    temp_path = f"uploads/temp_{file.filename}"
    with open(temp_path, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
        
    from app.services import ai_service
    data = ai_service.extract_cnic_details(temp_path)
    
    os.remove(temp_path)
    
    if not data['cnic']:
        raise HTTPException(status_code=400, detail="Could not extract CNIC details. Please try a clearer image.")
        
    return data

@router.get("/{customer_id}")
async def get_customer_status(customer_id: int):
    cust = db.get_customer_by_id(customer_id)
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    conn = db.get_conn()
    conn.row_factory = db.sqlite3.Row
    cursor = conn.cursor()
    
    verif = cursor.execute("SELECT * FROM Verifications WHERE customer_id = ?", (customer_id,)).fetchone()
    loan = cursor.execute("SELECT * FROM LoanEligibility WHERE customer_id = ?", (customer_id,)).fetchone()
    
    conn.close()
    
    return {
        "customer": cust,
        "verification": dict(verif) if verif else None,
        "loan": dict(loan) if loan else None
    }
