import os
import shutil
from app.db import insert_document

UPLOAD_DIR = os.path.join('data', 'docs')
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf'}
MAX_FILE_SIZE_MB = 5

def allowed_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def save_uploaded_file(customer_id, file_path, doc_type):
    """
    Saves a file to the customer's document folder and updates the DB.
    file_path: The path to the temporary or source file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Source file not found: {file_path}")

    if not allowed_file(file_path):
        raise ValueError(f"File type not allowed. Allowed: {ALLOWED_EXTENSIONS}")

    # Check size
    if os.path.getsize(file_path) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise ValueError(f"File too large. Max size: {MAX_FILE_SIZE_MB}MB")

    # Create customer dir
    customer_dir = os.path.join(UPLOAD_DIR, str(customer_id))
    os.makedirs(customer_dir, exist_ok=True)

    # Generate new filename
    filename = os.path.basename(file_path)
    dest_path = os.path.join(customer_dir, f"{doc_type}_{filename}")
    
    # Copy file
    shutil.copy2(file_path, dest_path)

    # Update DB
    insert_document(customer_id, doc_type, dest_path)
    return dest_path
