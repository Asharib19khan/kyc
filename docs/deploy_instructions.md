# Deployment Instructions

## 1. Prerequisites
*   Windows 10/11
*   Python 3.9+
*   Tesseract OCR installed (Add to PATH)

## 2. Installation
1.  Clone the repository.
2.  Create a virtual environment:
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Initialize Database:
    ```bash
    python -m app.db
    python -m app.auth
    ```

## 3. Building Executables (EXE)
To create standalone executables for distribution:

1.  Install PyInstaller:
    ```bash
    pip install pyinstaller
    ```
2.  Build Customer App:
    ```bash
    pyinstaller --noconsole --onefile --name KYC_Registration app/gui_registration.py
    ```
3.  Build Admin App:
    ```bash
    pyinstaller --noconsole --onefile --name KYC_Admin app/gui_admin.py
    ```
4.  **Output**: The `.exe` files will be in the `dist/` folder.

## 4. Distribution
*   Copy the `dist/KYC_Registration.exe` and `dist/KYC_Admin.exe` to the target machine.
*   **Important**: You must also copy the `data/` folder (or ensure the app creates it) and `Tesseract-OCR` if not installed globally.
*   For best results, keep the folder structure:
    ```
    /KYC_System
      /data
      KYC_Registration.exe
      KYC_Admin.exe
    ```
