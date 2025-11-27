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
    dob: Optional[str] = Form(None),
    father_name: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None)
):
    # --- FAIL-SAFE REGISTRATION ---
    # We wrap everything in a try-except to ensure the user is ALWAYS created
    # even if advanced features (Risk Engine, AI, etc.) fail.
    
    try:
        print(f"Registering user: {full_name}, {email}")
        
        # 1. Calculate Initial Risk Profile (Safe Mode)
        risk_profile = {
            'risk_score': 30,
            'trust_score': 70,
            'segment': 'Standard',
            'reasons': ['Initial Registration']
        }
        
        try:
            from app.services import risk_engine
            import random
            
            # Fetch existing customers for duplicate check
            conn = db.get_conn()
            conn.row_factory = db.sqlite3.Row
            cursor = conn.cursor()
            rows = cursor.execute("SELECT id, full_name, cnic, email, phone FROM Customers").fetchall()
            conn.close()
            
            # Decrypt sensitive data (Safe)
            existing_customers = []
            for row in rows:
                try:
                    cust = dict(row)
                    cust['cnic'] = security_utils.decrypt_data(cust['cnic'])
                    cust['phone'] = security_utils.decrypt_data(cust['phone'])
                    existing_customers.append(cust)
                except:
                    pass

            cust_data = {
                "email": email, "address": address, "cnic": cnic,
                "phone": phone, "income_range": income_range, "full_name": full_name
            }
            
            risk_profile = risk_engine.calculate_risk_profile(
                cust_data,
                existing_customers=existing_customers,
                face_match_score=random.randint(60, 99)
            )
        except Exception as e:
            print(f"⚠️ Risk Engine Failed: {e}. Proceeding with default values.")

        # 2. Hash Password
        from app import auth
        hashed_pw = auth.hash_password(password)

        # 3. Insert Customer (CRITICAL STEP)
        print("Inserting customer into DB...")
        cust_id, customer_code = db.insert_customer(
            full_name, cnic, email, phone, address, income_range, hashed_pw,
            trust_score=risk_profile['trust_score'],
            segment=risk_profile['segment']
        )
        print(f"✅ Customer inserted: ID {cust_id}, Code {customer_code}")
        
        # 4. Post-Registration Tasks (Non-Critical)
        try:
            # Loan Eligibility
            from app.services import risk_engine
            loan_eligibility = risk_engine.assess_loan_eligibility(risk_profile['risk_score'], income_range)
            db.save_loan_eligibility(
                cust_id, risk_profile['risk_score'], income_range,
                loan_eligibility['status'], loan_eligibility['max_limit']
            )
            
            # Verification Record
            ai_recommendations = []
            if risk_profile['risk_score'] > 70: ai_recommendations.append("⚠️ HIGH RISK")
            
            base_analysis = f"AI Analysis: {', '.join(risk_profile['reasons'])}" if risk_profile['reasons'] else "Initial Registration"
            auto_remarks = base_analysis + (" | " + " • ".join(ai_recommendations) if ai_recommendations else "")
            
            db.create_verification_record(
                cust_id, risk_score=risk_profile['risk_score'],
                trust_score=risk_profile['trust_score'], remarks=auto_remarks
            )
            
            # Mock Financials
            db.generate_mock_financials(cust_id)
            
        except Exception as e:
            print(f"⚠️ Post-registration tasks failed: {e}. Ignoring.")

        return {
            "status": "success",
            "customer_id": cust_id,
            "customer_code": customer_code,
            "message": f"Registration successful! Your code: {customer_code}"
        }

    except Exception as e:
        # GLOBAL FALLBACK
        # If even the basic logic fails, we try one last desperate insert
        print(f"❌ CRITICAL REGISTRATION ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        try:
            # Emergency Insert
            from app import auth
            hashed_pw = auth.hash_password(password)
            cust_id, customer_code = db.insert_customer(
                full_name, cnic, email, phone, address, income_range, hashed_pw
            )
            return {
                "status": "success",
                "customer_id": cust_id,
                "customer_code": customer_code,
                "message": f"Registration successful (Recovery Mode)! Your code: {customer_code}"
            }
        except Exception as final_e:
            raise HTTPException(status_code=500, detail=f"Registration Failed: {str(e)}")

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
