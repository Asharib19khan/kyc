from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app import db
from app.api.auth import oauth2_scheme
from app import security_utils
from datetime import datetime, timedelta
import io
import csv

router = APIRouter()

@router.get("/reports/stats")
async def get_report_stats(time_range: str = "24 Hours", token: str = Depends(oauth2_scheme)):
    """
    Get verification statistics for reports page
    """
    conn = db.get_conn()
    cursor = conn.cursor()
    
    # Get overall status counts
    total_verified = cursor.execute("SELECT COUNT(*) FROM Verifications WHERE status='Verified'").fetchone()[0]
    total_rejected = cursor.execute("SELECT COUNT(*) FROM Verifications WHERE status='Rejected'").fetchone()[0]
    total_pending = cursor.execute("SELECT COUNT(*) FROM Verifications WHERE status='Pending'").fetchone()[0]
    
    # Get daily activity for last 7 days (for bar chart)
    daily_stats = []
    for i in range(6, -1, -1):
        date = datetime.now() - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        day_name = date.strftime('%a')
        
        verified = cursor.execute(
            "SELECT COUNT(*) FROM Verifications WHERE status='Verified' AND date(date) = ?",
            (date_str,)
        ).fetchone()[0]
        
        rejected = cursor.execute(
            "SELECT COUNT(*) FROM Verifications WHERE status='Rejected' AND date(date) = ?",
            (date_str,)
        ).fetchone()[0]
        
        daily_stats.append({
            "name": day_name,
            "verified": verified,
            "rejected": rejected
        })
    
    conn.close()
    
    return {
        "overall": {
            "verified": total_verified,
            "rejected": total_rejected,
            "pending": total_pending
        },
        "daily_activity": daily_stats
    }

@router.get("/reports/export/{status}")
async def export_customers(status: str, token: str = Depends(oauth2_scheme)):
    """
    Export customers as CSV based on verification status
    """
    conn = db.get_conn()
    cursor = conn.cursor()
    
    # Map status to database value
    status_map = {
        "verified": "Verified",
        "rejected": "Rejected",
        "pending": "Pending"
    }
    
    db_status = status_map.get(status.lower())
    if not db_status:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    # Get customers with verification data
    query = """
        SELECT 
            c.id,
            c.full_name,
            c.cnic,
            c.email,
            c.phone,
            c.address,
            v.status,
            v.risk_score,
            v.trust_score,
            v.date,
            v.remarks
        FROM Customers c
        JOIN Verifications v ON c.id = v.customer_id
        WHERE v.status = ?
        ORDER BY v.date DESC
    """
    
    customers = cursor.execute(query, (db_status,)).fetchall()
    conn.close()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'ID', 'Full Name', 'CNIC', 'Email', 'Phone', 'Address',
        'Status', 'Risk Score', 'Trust Score', 'Date', 'Remarks'
    ])
    
    # Write data
    for cust in customers:
        try:
            decrypted_cnic = security_utils.decrypt_data(cust['cnic'])
        except:
            decrypted_cnic = cust['cnic']
        
        try:
            decrypted_email = security_utils.decrypt_data(cust['email'])
        except:
            decrypted_email = cust['email']
        
        try:
            decrypted_phone = security_utils.decrypt_data(cust['phone'])
        except:
            decrypted_phone = cust['phone']
        
        writer.writerow([
            cust['id'],
            cust['full_name'],
            decrypted_cnic,
            decrypted_email,
            decrypted_phone,
            cust['address'],
            cust['status'],
            cust['risk_score'],
            cust['trust_score'],
            cust['date'],
            cust['remarks']
        ])
    
    # Create response
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={status}_customers_{datetime.now().strftime('%Y%m%d')}.csv"
        }
    )
