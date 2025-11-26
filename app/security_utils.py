import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Constants
KEY_FILE = "secret.key"
SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32 # 256 bits for AES-256

def load_key():
    """Loads the encryption key or generates a new one if it doesn't exist."""
    if not os.path.exists(KEY_FILE):
        # Generate a random 32-byte key for AES-256
        key = AESGCM.generate_key(bit_length=256)
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
    else:
        with open(KEY_FILE, "rb") as key_file:
            key = key_file.read()
            
    if len(key) != KEY_SIZE:
        raise ValueError(f"Invalid key length: {len(key)}. Expected {KEY_SIZE} bytes for AES-256.")
        
    return key

# Initialize Cipher
# Note: In a real production app, you might want to rotate keys or use a KMS.
# For this implementation, we load the key once.
MASTER_KEY = load_key()
aesgcm = AESGCM(MASTER_KEY)

def encrypt_data(data: str) -> str:
    """
    Encrypts a string using AES-256-GCM.
    Returns a base64 encoded string containing the nonce and ciphertext.
    Format: base64(nonce + ciphertext + tag)
    Note: AESGCM.encrypt appends the tag automatically.
    """
    if not data:
        return data
        
    nonce = os.urandom(NONCE_SIZE)
    # encrypt(nonce, data, associated_data)
    ciphertext = aesgcm.encrypt(nonce, data.encode('utf-8'), None)
    
    # Combine nonce + ciphertext (which includes tag)
    encrypted_payload = nonce + ciphertext
    return base64.urlsafe_b64encode(encrypted_payload).decode('utf-8')

def decrypt_data(token: str) -> str:
    """
    Decrypts a base64 encoded string using AES-256-GCM.
    Expects format: base64(nonce + ciphertext + tag)
    """
    if not token:
        return token
        
    try:
        decoded_payload = base64.urlsafe_b64decode(token)
        
        if len(decoded_payload) < NONCE_SIZE + 16: # Min length check
            return "[INVALID DATA]"
            
        nonce = decoded_payload[:NONCE_SIZE]
        ciphertext = decoded_payload[NONCE_SIZE:]
        
        return aesgcm.decrypt(nonce, ciphertext, None).decode('utf-8')
    except Exception as e:
        # Log error in production
        print(f"Decryption error: {e}")
        return "[ENCRYPTED]"
