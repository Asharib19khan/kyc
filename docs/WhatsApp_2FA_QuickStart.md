# WhatsApp 2FA Quick Start

## ✅ What You Need

1. **Twilio Account** - You have this ✓
2. **WhatsApp Number** - +923130028473 ✓
3. **Twilio Credentials** - Need to add these

## 🚀 Setup Steps (5 minutes)

### Step 1: Get Twilio Credentials
1. Go to https://console.twilio.com/
2. Copy your **Account SID** (starts with "AC...")
3. Copy your **Auth Token** (click eye icon to reveal)

### Step 2: Join WhatsApp Sandbox
1. In Twilio Console → **Messaging** → **Try it out** → **Send a WhatsApp message**
2. You'll see a number like `+1 415 523 8886`
3. You'll see a code like `join abc-xyz`
4. **On your phone**: Open WhatsApp, send that code to that number
5. Wait for confirmation message

### Step 3: Update config.py
Open `c:\Users\pc\Desktop\KYC_Verification_System\config.py` and update:

```python
TWILIO_ACCOUNT_SID = "ACxxxxxxxxxxxxx"  # ← Paste your Account SID here
TWILIO_AUTH_TOKEN = "your_auth_token"   # ← Paste your Auth Token here
```

### Step 4: Restart Backend
The backend will auto-reload, or press Ctrl+C and run:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Step 5: Test!
1. Go to login page
2. Enter admin credentials
3. Click Next
4. **Check your WhatsApp** - you should receive the code!
5. Enter code and login

## 📱 Expected WhatsApp Message

```
🔐 Your NeoBank Admin Verification Code is: 123456

This code will expire in 5 minutes.
```

## ❓ Troubleshooting

**Not receiving WhatsApp?**
- Did you join the sandbox? (Step 2)
- Check backend logs for errors
- Verify credentials in config.py

**Still not working?**
- Check `code.txt` file for the code
- The system will fallback to email if WhatsApp fails
- Backend logs will show which method succeeded

## 🔄 Fallback Chain

1. **WhatsApp** (Primary) → Your phone
2. **Email** (Fallback) → k255570@nu.edu.pk  
3. **File** (Last resort) → code.txt

At least one will always work!
