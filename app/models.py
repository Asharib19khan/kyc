from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

# --- Auth Models ---
class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: int
    full_name: str

# --- KYC Models ---
class CustomerCreate(BaseModel):
    full_name: str
    cnic: str = Field(..., min_length=13, max_length=15)
    email: EmailStr
    phone: str
    address: str
    income_range: str
    
class LocationData(BaseModel):
    latitude: float
    longitude: float

# --- Admin Models ---
class AdminCreate(BaseModel):
    username: str
    password: str
    full_name: str

class VerificationUpdate(BaseModel):
    status: str
    remarks: Optional[str] = None
    risk_score: int
    trust_score: int
