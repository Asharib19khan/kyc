# NeoBank KYC Verification System

A secure KYC (Know Your Customer) verification system with admin and customer portals.

## Features

- 🔐 **2FA Authentication** - WhatsApp-based two-factor authentication
- 📱 **Progressive Web App** - Installable on mobile devices
- 🏦 **Customer Portal** - KYC submission and loan applications
- 👨‍💼 **Admin Portal** - Verification management and audit logs
- 🔒 **Secure** - AES-256-GCM encryption, bcrypt password hashing

## Tech Stack

**Frontend:**
- React + Vite
- TailwindCSS
- Lucide Icons

**Backend:**
- Python FastAPI
- SQLite Database
- Twilio API (WhatsApp)

## Deployment

### Frontend (Vercel)
1. Push to GitHub
2. Import repository in Vercel
3. Set framework: Vite
4. Deploy

### Backend (Render)
1. Create new Web Service on Render
2. Connect GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (see below)
6. Enable persistent disk for `/opt/render/project/src/data` (1GB)

### Environment Variables (Render)

```env
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
ADMIN_WHATSAPP_NUMBER=whatsapp:+92XXXXXXXXXX
EMAIL_SENDER=your_email@example.com
EMAIL_APP_PASSWORD=your_app_password
```

## Local Development

**Backend:**
```bash
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## License

MIT
