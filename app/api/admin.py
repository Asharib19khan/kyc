from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from app import db, models
from app.api.auth import oauth2_scheme, get_current_user
import os

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(token: str = Depends(oauth2_scheme)):
    conn = db.get_conn()
    cursor = conn.cursor()
    
    total_customers = cursor.execute("SELECT COUNT(*) FROM Customers").fetchone()[0]
    pending_verifications = cursor.execute("SELECT COUNT(*) FROM Verifications WHERE status='Pending'").fetchone()[0]
    approved_loans = cursor.execute("SELECT COUNT(*) FROM LoanEligibility WHERE eligibility_status='Auto-Approved'").fetchone()[0]
    
    conn.close()
    
    return {
        "total_customers": total_customers,
        "pending_verifications": pending_verifications,
        "approved_loans": approved_loans
    }

@router.get("/pending")
async def get_pending_verifications(token: str = Depends(oauth2_scheme)):
    return db.get_pending_customers()

@router.get("/all-verifications")
async def get_all_verifications(token: str =Depends(oauth2_scheme)):
    """
    Returns ALL verifications (Pending + Verified) with AI risk scores and fraud detection
    """
    from app.services import risk_engine
    from app import ai_utils, security_utils
    
    conn = db.get_conn()
    cursor = conn.cursor()
    
    query = """
        SELECT 
            c.id,
            c.full_name,
            c.cnic,
            c.email,
            c.phone,
            c.address,
            c.income_range,
            c.created_at,
            v.status,
            v.risk_score,
            v.trust_score,
            v.remarks,
            v.updated_at
        FROM Customers c
        LEFT JOIN Verifications v ON c.id = v.customer_id
        ORDER BY c.created_at DESC
    """
    
    customers = cursor.execute(query).fetchall()
    all_customers = cursor.execute("SELECT id, full_name, cnic FROM Customers").fetchall()
    conn.close()
    
    result = []
    for cust in customers:
        try:
            try:
                decrypted_cnic = security_utils.decrypt_data(cust['cnic'])
            except:
                decrypted_cnic = cust['cnic']
            
            # Decrypt phone and email if encrypted
            try:
                decrypted_phone = security_utils.decrypt_data(cust['phone'])
            except:
                decrypted_phone = cust['phone']
            
            try:
                decrypted_email = security_utils.decrypt_data(cust['email'])
            except:
                decrypted_email = cust['email']
            
            # Recalculate risk if pending or no score yet
            if not cust['risk_score'] or cust['status'] == 'Pending':
                try:
                    cust_dict = {
                        'full_name': cust['full_name'],
                        'cnic': decrypted_cnic,
                        'email': decrypted_email,
                        'phone': decrypted_phone,
                        'address': cust['address'],
                        'income_range': cust['income_range']
                    }
                    
                    risk_profile = risk_engine.calculate_risk_profile(cust_dict, existing_customers=all_customers)
                    fraud_score, fraud_alerts = ai_utils.check_fraud_rules(cust_dict)
                    final_risk_score = min(risk_profile['risk_score'] + fraud_score, 100)
                    is_fraud_flagged = fraud_score > 30 or final_risk_score > 70
                except Exception as e:
                    print(f"Error calculating risk for customer {cust['id']}: {e}")
                    # Use default values if calculation fails
                    final_risk_score = 50
                    fraud_alerts = []
                    is_fraud_flagged = False
            else:
                final_risk_score = cust['risk_score']
                fraud_alerts = []
                is_fraud_flagged = final_risk_score > 70
            
            result.append({
                'id': cust['id'],
                'serial_no': f"SN-{str(cust['id']).zfill(6)}",
                'full_name': cust['full_name'],
                'cnic': decrypted_cnic,
                'email': decrypted_email,
                'phone': decrypted_phone,
                'status': cust['status'] or 'Pending',
                'risk_score': final_risk_score,
                'trust_score': cust['trust_score'] or (100 - final_risk_score),
                'remarks': cust['remarks'] or '',
                'fraud_flagged': is_fraud_flagged,
                'fraud_alerts': fraud_alerts,
                'date': cust['updated_at'] or cust['created_at'],
                'created_at': cust['created_at'],
                'customer_id': cust['id']
            })
        except Exception as e:
            print(f"Error processing customer {cust.get('id', 'unknown')}: {e}")
            continue  # Skip this customer and continue with the next one
    
    
    return result

@router.post("/verify/{customer_id}")
async def verify_customer(customer_id: int, update: models.VerificationUpdate, token: str = Depends(oauth2_scheme)):
    cust = db.get_customer_by_id(customer_id)
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")

    from app.services import risk_engine
    risk_profile = risk_engine.calculate_risk_profile(cust)
    
    final_risk_score = risk_profile['risk_score']
    final_trust_score = risk_profile['trust_score']
    
    auto_remarks = f" | Auto-Analysis: {', '.join(risk_profile['reasons'])}" if risk_profile['reasons'] else ""
    final_remarks = f"{update.remarks}{auto_remarks}"

    db.update_verification(
        customer_id, 
        update.status, 
        final_risk_score, 
        final_trust_score, 
        final_remarks, 
        "Admin"
    )
    
    if update.status == "Verified":
        loan_eligibility = risk_engine.assess_loan_eligibility(final_risk_score, cust['income_range'])
        db.save_loan_eligibility(
            customer_id, 
            final_risk_score, 
            cust['income_range'],
            loan_eligibility['status'],
            loan_eligibility['max_limit']
        )
        
    return {"status": "success", "message": "Verification status updated"}

@router.get("/admins")
async def get_admins(token: str = Depends(oauth2_scheme)):
    conn = db.get_conn()
    cursor = conn.cursor()
    admins = cursor.execute("SELECT id, username, full_name, 'Active' as status, 'Super Admin' as role FROM Admins").fetchall()
    conn.close()
    return admins

@router.put("/profile")
async def update_admin_profile(data: dict, token: str = Depends(oauth2_scheme)):
    username = data.get('username')
    password = data.get('password')
    
    if not username:
        raise HTTPException(status_code=400, detail="Username required")
        
    conn = db.get_conn()
    cursor = conn.cursor()
    
    if password:
        from app import auth
        hashed_pw = auth.hash_password(password)
        cursor.execute("UPDATE Admins SET password_hash = ? WHERE username = ?",(hashed_pw, username))
    
    conn.commit()
    conn.close()
    
    return {"status": "success", "message": "Profile updated successfully"}

@router.get("/loans")
async def get_loan_applications(token: str = Depends(oauth2_scheme)):
    conn = db.get_conn()
    conn.row_factory = db.sqlite3.Row
    cursor = conn.cursor()
    
    query = """
        SELECT 
            le.id, 
            le.customer_id,
            c.full_name, 
            c.cnic,
            le.risk_score, 
            le.income_range, 
            le.eligibility_status, 
            le.max_limit,
            le.calculated_at
        FROM LoanEligibility le
        JOIN Customers c ON le.customer_id = c.id
        ORDER BY le.calculated_at DESC
    """
    rows = cursor.execute(query).fetchall()
    
    result = []
    from app import security_utils
    
    for row in rows:
        r = dict(row)
        try:
            r['cnic'] = security_utils.decrypt_data(r['cnic'])
        except:
            pass
        result.append(r)
        
    conn.close()
    return result

@router.get("/loans/{loan_id}/details")
async def get_loan_details(loan_id: int, token: str = Depends(oauth2_scheme)):
    conn = db.get_conn()
    conn.row_factory = db.sqlite3.Row
    cursor = conn.cursor()
    
    loan = cursor.execute("SELECT * FROM LoanEligibility WHERE id = ?", (loan_id,)).fetchone()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    customer_id = loan['customer_id']
    cust = db.get_customer_by_id(customer_id)
    docs = cursor.execute("SELECT doc_type, file_path FROM Documents WHERE customer_id = ?", (customer_id,)).fetchall()
    verif = cursor.execute("SELECT * FROM Verifications WHERE customer_id = ?", (customer_id,)).fetchone()
    
    conn.close()
    
    return {
        "loan": dict(loan),
        "customer": cust,
        "documents": [dict(d) for d in docs],
        "verification": dict(verif) if verif else None
    }

@router.post("/loan-decision")
async def make_loan_decision(decision_data: dict, token: str = Depends(oauth2_scheme)):
    loan_id = decision_data.get('loan_id')
    decision = decision_data.get('decision')
    reason = decision_data.get('reason')
    
    if not loan_id or decision not in ["Approved", "Rejected"]:
        raise HTTPException(status_code=400, detail="Invalid decision data")
        
    conn = db.get_conn()
    conn.row_factory = db.sqlite3.Row
    cursor = conn.cursor()
    
    loan = cursor.execute("SELECT * FROM LoanEligibility WHERE id = ?", (loan_id,)).fetchone()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
        
    customer_id = loan['customer_id']
    cust = db.get_customer_by_id(customer_id)
    
    new_status = "Approved" if decision == "Approved" else "Rejected"
    cursor.execute("UPDATE LoanEligibility SET eligibility_status = ? WHERE id = ?", (new_status, loan_id))
    
    v_status = "Verified" if decision == "Approved" else "Rejected"
    cursor.execute("UPDATE Verifications SET status = ?, remarks = ? WHERE customer_id = ?", (v_status, reason, customer_id))
    
    conn.commit()
    conn.close()
    
    from app.services import pdf_service
    pdf_path = pdf_service.generate_loan_decision_pdf(
        cust, 
        decision, 
        reason, 
        "Admin User",
        max_limit=loan['max_limit'] if decision == "Approved" else 0
    )
    
    return {"status": "success", "message": f"Loan {decision}", "pdf_url": pdf_path}

@router.get("/download-pdf")
async def download_pdf(path: str):
    if os.path.exists(path):
        return FileResponse(path, media_type='application/pdf', filename=os.path.basename(path))
    raise HTTPException(status_code=404, detail="File not found")

@router.delete("/verifications/{customer_id}")
async def delete_verification(customer_id: int, token: str = Depends(oauth2_scheme)):
    conn = db.get_conn()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM Verifications WHERE customer_id = ?", (customer_id,))
        cursor.execute("DELETE FROM LoanEligibility WHERE customer_id = ?", (customer_id,))
        cursor.execute("DELETE FROM Documents WHERE customer_id = ?", (customer_id,))
        cursor.execute("DELETE FROM Customers WHERE id = ?", (customer_id,))
        conn.commit()
        return {"status": "success", "message": "Customer and verification record deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to delete record")
    finally:
        conn.close()

@router.get("/audit-logs")
async def get_audit_logs(token: str = Depends(oauth2_scheme)):
    conn = db.get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM AuditLog ORDER BY timestamp DESC LIMIT 10")
    logs = cursor.fetchall()
    conn.close()
    return logs

@router.get("/settings")
async def get_settings(current_user: str = Depends(get_current_user)):
    return db.get_admin_settings(current_user)

@router.post("/settings")
async def update_settings(settings: dict, current_user: str = Depends(get_current_user)):
    db.update_admin_settings(current_user, settings)
    return {"status": "success", "message": "Settings updated"}
