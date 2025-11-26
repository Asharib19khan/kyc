# --- EMAIL CONFIGURATION ---
# To enable Real 2FA, you must fill these details.
# 1. Go to your Google Account > Security > 2-Step Verification > App Passwords.
# 2. Generate a new App Password (select 'Mail' and 'Windows Computer').
# 3. Paste the 16-character password below (no spaces).

import os

# --- EMAIL CONFIGURATION ---
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "your_email@example.com")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD", "your_app_password")

# --- TWILIO CONFIGURATION (For WhatsApp 2FA) ---
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "your_account_sid")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "your_auth_token")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
ADMIN_WHATSAPP_NUMBER = os.getenv("ADMIN_WHATSAPP_NUMBER", "whatsapp:+92XXXXXXXXXX")

# --- DEV CONFIGURATION ---
USE_FIXED_2FA = False
FIXED_2FA_CODE = "123456"
