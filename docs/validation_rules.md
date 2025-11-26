# Input Validation Rules

## 1. Personal Information
*   **Full Name**: Alphabets and spaces only. Min 3 chars.
*   **CNIC**: Format `XXXXX-XXXXXXX-X` (13 digits + 2 hyphens).
*   **Phone**: Format `03XXXXXXXXX` (11 digits, starts with 03).
*   **Email**: Valid email format (regex).
*   **Income Range**: Selected from dropdown (e.g., "Below 50k", "50k-100k", "Above 100k").

## 2. Documents
*   **Allowed Types**: `.jpg`, `.jpeg`, `.png`, `.pdf`.
*   **Max Size**: 5MB.
*   **Required Files**:
    1.  CNIC Front
    2.  CNIC Back
    3.  Selfie (for liveness check)

## 3. Business Logic
*   **Duplicate CNIC**: Rejected immediately (DB Constraint).
*   **Age**: Must be 18+ (derived from CNIC if possible, or manual check).
