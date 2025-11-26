import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app import config

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(receiver_email, otp):
    """
    Sends a Real OTP to the receiver_email using credentials from config.py.
    Returns True if successful, False otherwise.
    """
    sender_email = config.SENDER_EMAIL
    password = config.APP_PASSWORD.replace(" ", "") # Remove spaces if any
    
    if "your_email" in sender_email:
        print("Error: Email Config not set.")
        return False

    subject = "Your Admin Login OTP - NeoBank Secure"
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: auto; border: 1px solid #ddd; padding: 20px; border-radius: 10px;">
            <h2 style="color: #2c3e50; text-align: center;">NeoBank Security Alert</h2>
            <p>Dear Admin,</p>
            <p>A login attempt was detected for your account.</p>
            <div style="background-color: #f1f2f6; padding: 15px; text-align: center; font-size: 24px; font-weight: bold; letter-spacing: 5px; color: #2980b9; margin: 20px 0;">
                {otp}
            </div>
            <p>Please enter this code to complete your login. This code expires in 5 minutes.</p>
            <p style="font-size: 12px; color: #7f8c8d; text-align: center; margin-top: 30px;">
                If you did not request this, please contact IT Security immediately.
            </p>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = "NeoBank Security <noreply@neobank.com>"
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        # Connect to Gmail SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        print(f"OTP Sent to {receiver_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
