# 2FA Email Workaround

## Issue
Email delivery for 2FA codes is currently not working due to SMTP authentication issues with the nu.edu.pk email account.

## Workaround
The system automatically writes the 2FA code to a file called `code.txt` in the project root directory as a fallback.

### Steps to Login:
1. On the login page, enter your admin credentials (username: `admin`, password: `admin123`)
2. Click "Next" to proceed to the 2FA step
3. **Open the file**: `c:\Users\pc\Desktop\KYC_Verification_System\code.txt`
4. Copy the 6-digit code from the file
5. Paste it into the "Verification Code" field on the 2FA page
6. Click "Verify & Login"

## Current 2FA Code
The latest generated code is: **895439**

## Permanent Fix Needed
To fix email delivery permanently, you need to:

1. **Verify App Password**: Make sure the app password `qjaq epdz rxgp upev` is correct and active for your nu.edu.pk email
2. **Check Email Settings**: Ensure your nu.edu.pk account allows SMTP access via Office365
3. **Alternative**: Consider using a Gmail account instead, which has more reliable SMTP support

### To Use Gmail Instead:
1. Create a Gmail account or use an existing one
2. Enable 2-Step Verification in Gmail settings
3. Generate an App Password for "Mail" 
4. Update lines 159-160 in `app/api/auth.py` with your Gmail address and app password
5. Change line 174 back to `smtp.gmail.com` instead of `smtp.office365.com`
