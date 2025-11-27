from fastapi import APIRouter, HTTPException, Depends, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app import auth, db, models, security_utils
import jwt
from datetime import datetime, timedelta

router = APIRouter()

# JWT Configuration
SECRET_KEY = security_utils.MASTER_KEY.hex() # Use the encryption key as JWT secret for simplicity, or generate another.
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Simple in-memory store for OTPs
OTP_STORE = {}

@router.post("/token", response_model=models.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = db.get_conn()
    cursor = conn.cursor()
    
    # 1. Check Admin
    # print(f"DEBUG: Login attempt for username: {form_data.username}")
    admin_user = cursor.execute("SELECT * FROM Admins WHERE username = ?", (form_data.username,)).fetchone()
    
    if admin_user:
        # print(f"DEBUG: Admin found: {admin_user['username']}")
        if auth.check_password(admin_user['password_hash'], form_data.password):
        if auth.check_password(admin_user['password_hash'], form_data.password):
            # 2FA DISABLED BY USER REQUEST
            # Direct login for admin
            token = create_access_token({"sub": admin_user['username'], "role": "admin", "id": admin_user['id']})
            return {"access_token": token, "token_type": "bearer", "role": "admin", "user_id": admin_user['id'], "full_name": admin_user['full_name']}
        else:
            pass # Password mismatch
        else:
            pass # Password mismatch
    else:
        pass # Admin not found

    # 2. Check Customer (Login by CNIC + Customer Code)
    # Customer login requires: CNIC (username), Password, and Customer Code (client_secret)
    
    # Extract customer code from client_secret field
    customer_code = form_data.client_secret if hasattr(form_data, 'client_secret') else None
    
    if not customer_code:
        # For backward compatibility, check if it's in the form data
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Customer code required for login",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    conn = db.get_conn()
    cursor = conn.cursor()
    all_customers = cursor.execute("SELECT id, cnic, full_name, password_hash, customer_code FROM Customers").fetchall()
    
    found_customer = None
    for cust in all_customers:
        try:
            stored_cnic = cust['cnic']
            decrypted_cnic = security_utils.decrypt_data(stored_cnic)
            
            # Check CNIC, Password, AND Customer Code
            if decrypted_cnic == form_data.username:
                if auth.check_password(cust['password_hash'], form_data.password):
                    if cust['customer_code'] == customer_code:
                        found_customer = cust
                        break
        except Exception as e:
            continue
            
    conn.close()

    if found_customer:
        token = create_access_token({"sub": form_data.username, "role": "customer", "id": found_customer['id']})
        return {"access_token": token, "token_type": "bearer", "role": "customer", "user_id": found_customer['id'], "full_name": found_customer['full_name']}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    return username

@router.post("/admin/register", response_model=models.Token)
async def register_admin(user: models.AdminCreate):
    conn = db.get_conn()
    cursor = conn.cursor()
    existing = cursor.execute("SELECT * FROM Admins WHERE username = ?", (user.username,)).fetchone()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    auth.create_admin(user.username, user.password, user.full_name)
    
    token = create_access_token({"sub": user.username, "role": "admin", "id": 1})
    return {"access_token": token, "token_type": "bearer", "role": "admin", "user_id": 0, "full_name": user.full_name}

@router.post("/send-2fa")
async def send_2fa_code(username: str = Form(...)):
    # Check if admin exists
    conn = db.get_conn()
    cursor = conn.cursor()
    admin = cursor.execute("SELECT * FROM Admins WHERE username = ?", (username,)).fetchone()
    conn.close()

    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    # Generate Code
    import random
    from app import config
    
    if getattr(config, 'USE_FIXED_2FA', False):
        code = config.FIXED_2FA_CODE
        print(f"============================================")
        print(f"   🔐 DEV MODE 2FA CODE: {code}   ")
        print(f"============================================")
        OTP_STORE[username] = code
        # Simulate success for frontend
        return {"status": "sent", "message": f"Dev Mode: Use code {code}", "method": "dev", "debug_code": code}

    code = str(random.randint(100000, 999999))
    OTP_STORE[username] = code # Store it!
    
    print(f"============================================")
    print(f"   🔐 2FA CODE FOR {username}: {code}   ")
    print(f"============================================")
    
    with open("code.txt", "w") as f:
        f.write(code)
    
    # Try WhatsApp first, then email as fallback
    whatsapp_success = False
    email_success = False
    
    # 1. Try WhatsApp via Twilio
    try:
        from twilio.rest import Client
        
        client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
        
        message = client.messages.create(
            from_=config.TWILIO_WHATSAPP_FROM,
            body=f"🔐 Your NeoBank Admin Verification Code is: {code}\n\nThis code will expire in 5 minutes.",
            to=config.ADMIN_WHATSAPP_NUMBER
        )
        
        print(f"✅ WhatsApp sent! Message SID: {message.sid}")
        whatsapp_success = True
        
    except Exception as e:
        print(f"⚠️ WhatsApp sending failed: {e}")
        
        # 2. Fallback to Email
        try:
            import smtplib
            from email.mime.text import MIMEText
            
            sender_email = config.EMAIL_SENDER
            app_password = config.EMAIL_APP_PASSWORD
            
            msg = MIMEText(f"Your NeoBank Admin Verification Code is: {code}")
            msg['Subject'] = "NeoBank 2FA Code"
            msg['From'] = sender_email
            msg['To'] = sender_email
            
            s = smtplib.SMTP('smtp.office365.com', 587)
            s.starttls()
            s.login(sender_email, app_password)
            s.send_message(msg)
            s.quit()
            
            print(f"✅ Email sent to {sender_email}")
            email_success = True
            
        except Exception as email_error:
            print(f"⚠️ Email sending also failed: {email_error}")
    
    # Return appropriate response
    if whatsapp_success:
        return {"status": "sent", "message": "Code sent via WhatsApp", "method": "whatsapp", "debug_code": code}
    elif email_success:
        return {"status": "sent", "message": "Code sent via Email", "method": "email", "debug_code": code}
    else:
        return {"status": "error", "message": "Delivery failed. Check code.txt file.", "method": "file", "debug_code": code}

@router.post("/admin/register")
async def register_admin(data: dict, token: str = Depends(oauth2_scheme)):
    # In a real app, check if current user is Super Admin
    # For now, just allow any logged-in admin
    
    username = data.get('username')
    password = data.get('password')
    full_name = data.get('full_name')
    
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")
        
    conn = db.get_conn()
    cursor = conn.cursor()
    
    # Check existing
    existing = cursor.execute("SELECT * FROM Admins WHERE username = ?", (username,)).fetchone()
    if existing:
        conn.close()
        raise HTTPException(status_code=400, detail="Username already exists")
        
    # Hash Password
    hashed_pw = auth.hash_password(password)
    
    # Insert
    cursor.execute("INSERT INTO Admins (username, password_hash, full_name) VALUES (?, ?, ?)", 
                   (username, hashed_pw, full_name))
    conn.commit()
    conn.close()
    
    return {"status": "success", "message": "Admin created successfully"}

