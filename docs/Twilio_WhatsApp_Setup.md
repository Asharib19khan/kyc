# Twilio WhatsApp Setup Guide

## Step 1: Get Your Twilio Credentials

1. Go to [Twilio Console](https://console.twilio.com/)
2. Log in to your account
3. On the dashboard, you'll see:
   - **Account SID** (starts with "AC...")
   - **Auth Token** (click to reveal)
4. Copy both values

## Step 2: Set Up WhatsApp Sandbox

1. In Twilio Console, go to **Messaging** → **Try it out** → **Send a WhatsApp message**
2. You'll see a sandbox number (e.g., +1 415 523 8886)
3. You'll see a join code (e.g., "join abc-def")
4. **On your phone**: Open WhatsApp and send that join code to the sandbox number
5. You'll receive a confirmation message

## Step 3: Update Configuration

1. Open `config.py` in your project
2. Replace `your_account_sid_here` with your Account SID
3. Replace `your_auth_token_here` with your Auth Token
4. Update `TWILIO_WHATSAPP_FROM` if your sandbox number is different
5. Save the file

## Step 4: Test

1. Restart the backend server
2. Try logging in as admin
3. You should receive the 2FA code on WhatsApp!

## Troubleshooting

- **Not receiving messages?** Make sure you joined the sandbox by sending the join code
- **Authentication error?** Double-check your Account SID and Auth Token
- **Wrong number?** Verify the phone number format includes country code (+92 for Pakistan)

## Production Setup (Optional)

For production use:
1. Apply for WhatsApp Business API approval in Twilio
2. Get your own WhatsApp Business number
3. Update `TWILIO_WHATSAPP_FROM` with your approved number
