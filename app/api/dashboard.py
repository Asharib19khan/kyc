from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app import db, models, security_utils
from app.api.auth import oauth2_scheme, get_current_user
from app.services import pdf_service
import os

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats")
async def get_dashboard_stats(current_user: str = Depends(get_current_user)):
    conn = db.get_conn()
    conn.row_factory = db.sqlite3.Row
    cursor = conn.cursor()
    
    # Get all customers and decrypt CNICs to find the matching one
    all_customers = cursor.execute("SELECT * FROM Customers").fetchall()
    
    found_customer = None
    for cust in all_customers:
        try:
            decrypted_cnic = security_utils.decrypt_data(cust['cnic'])
            if decrypted_cnic == current_user:
                found_customer = cust
                break
        except:
            continue
    
    if not found_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    customer_id = found_customer['id']
    
    # Build customer dict with decrypted data
    cust_dict = dict(found_customer)
    try:
        cust_dict['cnic'] = security_utils.decrypt_data(found_customer['cnic'])
        cust_dict['phone'] = security_utils.decrypt_data(found_customer['phone'])
        cust_dict['address'] = security_utils.decrypt_data(found_customer['address'])
    except:
        pass
        
    # Get Verification Status
    verif = cursor.execute("SELECT * FROM Verifications WHERE customer_id = ?", (customer_id,)).fetchone()
    
    # Get ALL Loan Applications (for loan history)
    all_loan_apps = cursor.execute("SELECT * FROM LoanApplications WHERE customer_id = ? ORDER BY created_at DESC", (customer_id,)).fetchall()
    
    # Get Latest Loan Application (for dashboard banner)
    loan_app = cursor.execute("SELECT * FROM LoanApplications WHERE customer_id = ? ORDER BY created_at DESC LIMIT 1", (customer_id,)).fetchone()
    
    # Get Documents
    docs = cursor.execute("SELECT doc_type, file_path FROM Documents WHERE customer_id = ?", (customer_id,)).fetchall()
    
    # Get Unread Notifications Count
    notif_count = cursor.execute("SELECT COUNT(*) FROM Notifications WHERE customer_id = ? AND is_read = 0", (customer_id,)).fetchone()[0]
    
    conn.close()
    
    return {
        "customer": cust_dict,
        "verification": dict(verif) if verif else None,
        "loan_application": dict(loan_app) if loan_app else None,
        "loan_applications": [dict(app) for app in all_loan_apps],  # All loans for history
        "documents": [dict(d) for d in docs],
        "unread_notifications": notif_count
    }

@router.post("/loan/apply")
async def apply_for_loan(data: dict, current_user: str = Depends(get_current_user)):
    amount = data.get('amount')
    purpose = data.get('purpose')
    monthly_income = data.get('monthly_income')
    
    if not amount or not purpose or not monthly_income:
        raise HTTPException(status_code=400, detail="Missing required fields")
        
    conn = db.get_conn()
    cursor = conn.cursor()
    
    # Find customer by decrypting CNICs
    all_customers = cursor.execute("SELECT id, cnic FROM Customers").fetchall()
    customer_id = None
    for cust in all_customers:
        try:
            if security_utils.decrypt_data(cust['cnic']) == current_user:
                customer_id = cust['id']
                break
        except:
            continue
    
    if not customer_id:
        conn.close()
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Check if already has pending application
    existing = cursor.execute("SELECT id FROM LoanApplications WHERE customer_id = ? AND status = 'Pending'", (customer_id,)).fetchone()
    if existing:
        conn.close()
        raise HTTPException(status_code=400, detail="You already have a pending loan application")
        
    cursor.execute("""
        INSERT INTO LoanApplications (customer_id, amount, purpose, monthly_income, status)
        VALUES (?, ?, ?, ?, 'Pending')
    """, (customer_id, amount, purpose, monthly_income))
    
    # Add Notification
    cursor.execute("""
        INSERT INTO Notifications (customer_id, title, message)
        VALUES (?, 'Loan Application Submitted', 'Your loan application for PKR ' || ? || ' has been submitted successfully.')
    """, (customer_id, amount))
    
    conn.commit()
    conn.close()
    
    return {"status": "success", "message": "Loan application submitted"}

@router.get("/notifications")
async def get_notifications(current_user: str = Depends(get_current_user)):
    conn = db.get_conn()
    conn.row_factory = db.sqlite3.Row
    cursor = conn.cursor()
    
    # Find customer by decrypting CNICs
    all_customers = cursor.execute("SELECT id, cnic FROM Customers").fetchall()
    customer_id = None
    for cust in all_customers:
        try:
            if security_utils.decrypt_data(cust['cnic']) == current_user:
                customer_id = cust['id']
                break
        except:
            continue
    
    if not customer_id:
        conn.close()
        return []
    
    notifs = cursor.execute("SELECT * FROM Notifications WHERE customer_id = ? ORDER BY created_at DESC", (customer_id,)).fetchall()
    
    # Mark all as read
    cursor.execute("UPDATE Notifications SET is_read = 1 WHERE customer_id = ?", (customer_id,))
    conn.commit()
    conn.close()
    
    return [dict(n) for n in notifs]

@router.get("/messages")
async def get_messages(current_user: str = Depends(get_current_user)):
    conn = db.get_conn()
    conn.row_factory = db.sqlite3.Row
    cursor = conn.cursor()
    
    # Find customer by decrypting CNICs
    all_customers = cursor.execute("SELECT id, cnic FROM Customers").fetchall()
    customer_id = None
    for cust in all_customers:
        try:
            if security_utils.decrypt_data(cust['cnic']) == current_user:
                customer_id = cust['id']
                break
        except:
            continue
    
    if not customer_id:
        conn.close()
        return []
    
    msgs = cursor.execute("SELECT * FROM Messages WHERE customer_id = ? ORDER BY created_at DESC", (customer_id,)).fetchall()
    conn.close()
    
    return [dict(m) for m in msgs]

@router.get("/loan/download-pdf/{loan_id}")
async def download_loan_pdf(loan_id: int, current_user: str = Depends(get_current_user)):
    from fastapi.responses import FileResponse
    conn = db.get_conn()
    conn.row_factory = db.sqlite3.Row
    cursor = conn.cursor()
    
    # Find customer
    all_customers = cursor.execute("SELECT id, cnic, full_name FROM Customers").fetchall()
    customer_id = None
    customer_name = None
    for cust in all_customers:
        try:
            if security_utils.decrypt_data(cust['cnic']) == current_user:
                customer_id = cust['id']
                customer_name = cust['full_name']
                break
        except:
            continue
    
    if not customer_id:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Get loan application
    loan = cursor.execute("SELECT * FROM LoanApplications WHERE id = ? AND customer_id = ?", (loan_id, customer_id)).fetchone()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    # Get customer details for PDF
    customer = {
        'id': customer_id,
        'full_name': customer_name,
        'cnic': current_user,
        'email': 'N/A',
        'phone': 'N/A'
    }
    
    decision = loan['status']
    reason = loan['rejection_reason'] or 'N/A'
    max_limit = loan['amount'] if decision == 'Approved' else 0
    
    # Generate PDF
    pdf_path = pdf_service.generate_loan_decision_pdf(
        customer, decision, reason, "System Admin", max_limit
    )
    
    conn.close()
    
    return FileResponse(pdf_path, filename=f"Loan_{decision}_{loan_id}.pdf", media_type='application/pdf')
