from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
import os
from datetime import datetime

def generate_loan_decision_pdf(customer, decision, reason, admin_name, max_limit=0):
    """
    Generates a professional PDF for Loan Approval or Rejection.
    Returns the absolute file path of the generated PDF.
    """
    os.makedirs("generated_pdfs", exist_ok=True)
    filename = f"Loan_{decision}_{customer['id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    filepath = os.path.abspath(os.path.join("generated_pdfs", filename))
    
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    
    # --- Branding & Header ---
    # Draw Header Background
    c.setFillColor(HexColor("#4F46E5")) # Indigo-600
    c.rect(0, height - 100, width, 100, fill=1, stroke=0)
    
    # Bank Name/Logo
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("Helvetica-Bold", 30)
    c.drawString(50, height - 60, "NeoBank")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, "The Future of Banking")
    
    # Document Title
    c.setFillColor(HexColor("#000000"))
    c.setFont("Helvetica-Bold", 24)
    if decision == "Approved":
        c.setFillColor(HexColor("#16A34A")) # Green-600
        c.drawString(50, height - 150, "LOAN APPROVAL LETTER")
    else:
        c.setFillColor(HexColor("#DC2626")) # Red-600
        c.drawString(50, height - 150, "LOAN REJECTION NOTICE")
        
    # Meta Data
    c.setFillColor(HexColor("#000000"))
    c.setFont("Helvetica", 10)
    c.drawRightString(width - 50, height - 140, f"Date: {datetime.now().strftime('%B %d, %Y')}")
    c.drawRightString(width - 50, height - 155, f"Ref No: LN-{str(customer['id']).zfill(6)}")
    
    # --- Customer Details Box ---
    c.setStrokeColor(HexColor("#E5E7EB"))
    c.rect(50, height - 280, width - 100, 100, fill=0, stroke=1)
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(70, height - 200, "Applicant Details")
    
    c.setFont("Helvetica", 11)
    y = height - 225
    c.drawString(70, y, f"Name: {customer['full_name']}")
    c.drawString(300, y, f"CNIC: {customer['cnic']}")
    c.drawString(70, y - 20, f"Email: {customer['email']}")
    c.drawString(300, y - 20, f"Phone: {customer['phone']}")
    
    # --- Content Body ---
    y = height - 320
    c.setFont("Helvetica", 12)
    
    if decision == "Approved":
        c.drawString(50, y, f"Dear {customer['full_name']},")
        y -= 30
        c.drawString(50, y, "We are pleased to inform you that your loan application has been reviewed")
        y -= 20
        c.drawString(50, y, "and APPROVED by our credit committee.")
        
        y -= 50
        # Approval Box
        c.setFillColor(HexColor("#F0FDF4")) # Green-50
        c.setStrokeColor(HexColor("#16A34A"))
        c.rect(150, y - 60, width - 300, 80, fill=1, stroke=1)
        
        c.setFillColor(HexColor("#16A34A"))
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width / 2, y - 25, "Approved Amount")
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width / 2, y - 55, f"PKR {max_limit:,}")
        
        y -= 100
        c.setFillColor(HexColor("#000000"))
        c.setFont("Helvetica", 12)
        c.drawString(50, y, "Please login to your dashboard to view the disbursement schedule and")
        y -= 20
        c.drawString(50, y, "accept the terms and conditions.")
        
    else:
        c.drawString(50, y, f"Dear {customer['full_name']},")
        y -= 30
        c.drawString(50, y, "Thank you for your interest in NeoBank services.")
        y -= 20
        c.drawString(50, y, "After careful review, we regret to inform you that we are unable to approve")
        y -= 20
        c.drawString(50, y, "your loan application at this time.")
        
        y -= 50
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Reason for Rejection:")
        y -= 25
        c.setFont("Helvetica", 12)
        c.setFillColor(HexColor("#DC2626"))
        c.drawString(50, y, reason)
        
        y -= 50
        c.setFillColor(HexColor("#000000"))
        c.drawString(50, y, "You may re-apply after 30 days if your financial situation improves.")

    # --- Footer ---
    c.setStrokeColor(HexColor("#E5E7EB"))
    c.line(50, 100, width - 50, 100)
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 80, "Authorized Signatory")
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 65, f"Verified by: {admin_name}")
    
    c.setFont("Helvetica", 8)
    c.setFillColor(HexColor("#6B7280"))
    c.drawCentredString(width / 2, 40, "This is a computer-generated document. No physical signature is required.")
    c.drawCentredString(width / 2, 30, "NeoBank Ltd. | 123 Finance Avenue, Karachi, Pakistan | www.neobank.com")
    
    c.save()
    return filepath
