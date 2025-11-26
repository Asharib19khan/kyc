from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
import os
from datetime import datetime

def generate_loan_approval_pdf(customer_name, loan_amount, output_path=None):
    """Generates a professional Loan Approval Letter PDF."""
    
    if not output_path:
        # Save to Desktop by default
        desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        filename = f"Loan_Approval_{customer_name.replace(' ', '_')}.pdf"
        output_path = os.path.join(desktop, filename)
        
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    
    # Header / Logo Placeholder
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(colors.navy)
    c.drawString(1 * inch, height - 1 * inch, "NeoBank Enterprise")
    
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.gray)
    c.drawString(1 * inch, height - 1.2 * inch, "Secure KYC & Lending Division")
    
    # Line
    c.setStrokeColor(colors.navy)
    c.setLineWidth(2)
    c.line(1 * inch, height - 1.4 * inch, width - 1 * inch, height - 1.4 * inch)
    
    # Date
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    c.drawString(width - 2.5 * inch, height - 2 * inch, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    
    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 3 * inch, "OFFICIAL LOAN APPROVAL NOTICE")
    
    # Body
    text_y = height - 4 * inch
    c.setFont("Helvetica", 12)
    
    lines = [
        f"Dear {customer_name},",
        "",
        "We are pleased to inform you that your application for a personal loan has been",
        "APPROVED based on your excellent credit score and verified income.",
        "",
        "Loan Details:",
        f"   • Approved Amount: PKR {loan_amount:,.2f}",
        "   • Interest Rate: 12% APR",
        "   • Term: 12 Months",
        "",
        "Next Steps:",
        "Please visit your nearest branch or login to your dashboard to sign the",
        "digital agreement and receive the funds within 24 hours.",
        "",
        "Thank you for choosing NeoBank.",
        "",
        "Sincerely,",
        "The Credit Risk Team"
    ]
    
    for line in lines:
        c.drawString(1 * inch, text_y, line)
        text_y -= 0.25 * inch
        
    # Footer
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(colors.gray)
    c.drawCentredString(width / 2, 0.5 * inch, "This is a computer-generated document and does not require a signature.")
    c.drawCentredString(width / 2, 0.35 * inch, "NeoBank Enterprise | 123 Fintech Ave, Cyber City | support@neobank.com")
    
    c.save()
    return output_path
