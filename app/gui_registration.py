import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from app import db, utils

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class RegistrationApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("KYC & Loan Registration")
        self.geometry("600x800")

        self.files = {
            "CNIC_Front": None,
            "CNIC_Back": None,
            "Selfie": None
        }

        self.create_widgets()

    def create_widgets(self):
        # Title
        self.label_title = ctk.CTkLabel(self, text="Customer Registration", font=("Roboto", 24, "bold"))
        self.label_title.pack(pady=20)

        # Form Frame
        self.frame_form = ctk.CTkFrame(self)
        self.frame_form.pack(pady=10, padx=20, fill="both", expand=True)

        # Inputs
        self.entry_name = self.create_input("Full Name")
        self.entry_cnic = self.create_input("CNIC (e.g. 42101-1234567-1)")
        self.entry_email = self.create_input("Email")
        self.entry_phone = self.create_input("Phone (03XXXXXXXXX)")
        self.entry_address = self.create_input("Address")
        
        # Income Dropdown
        self.label_income = ctk.CTkLabel(self.frame_form, text="Monthly Income Range")
        self.label_income.pack(pady=(10, 0), padx=20, anchor="w")
        self.combo_income = ctk.CTkComboBox(self.frame_form, values=["Below 50k", "50k-100k", "100k-200k", "Above 200k"])
        self.combo_income.pack(pady=(5, 10), padx=20, fill="x")

        # File Uploads
        self.create_upload_btn("Upload CNIC Front", "CNIC_Front")
        self.create_upload_btn("Upload CNIC Back", "CNIC_Back")
        self.create_upload_btn("Upload Selfie", "Selfie")

        # Submit Button
        self.btn_submit = ctk.CTkButton(self, text="Submit Application", command=self.submit_form, height=40, font=("Roboto", 16, "bold"))
        self.btn_submit.pack(pady=20, padx=20, fill="x")

    def create_input(self, placeholder):
        entry = ctk.CTkEntry(self.frame_form, placeholder_text=placeholder, height=35)
        entry.pack(pady=10, padx=20, fill="x")
        return entry

    def create_upload_btn(self, text, key):
        frame = ctk.CTkFrame(self.frame_form, fg_color="transparent")
        frame.pack(pady=5, padx=20, fill="x")
        
        lbl = ctk.CTkLabel(frame, text=text, width=150, anchor="w")
        lbl.pack(side="left")
        
        btn = ctk.CTkButton(frame, text="Choose File", width=100, command=lambda: self.upload_file(key, lbl_status))
        btn.pack(side="right")
        
        lbl_status = ctk.CTkLabel(frame, text="No file selected", text_color="gray", font=("Arial", 10))
        lbl_status.pack(side="right", padx=10)

    def upload_file(self, key, label_widget):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg;*.jpeg;*.png"), ("PDF", "*.pdf")])
        if path:
            self.files[key] = path
            label_widget.configure(text=os.path.basename(path), text_color="green")

    def submit_form(self):
        # Basic Validation
        name = self.entry_name.get()
        cnic = self.entry_cnic.get()
        email = self.entry_email.get()
        phone = self.entry_phone.get()
        address = self.entry_address.get()
        income = self.combo_income.get()

        if not all([name, cnic, email, phone, address]):
            messagebox.showerror("Error", "All fields are required.")
            return

        if not all(self.files.values()):
            messagebox.showerror("Error", "Please upload all required documents.")
            return

        try:
            # 1. Insert Customer
            cust_id = db.insert_customer(name, cnic, email, phone, address, income)
            
            # 2. Save Files
            for doc_type, path in self.files.items():
                utils.save_uploaded_file(cust_id, path, doc_type)

            # 3. Create Verification & Loan Record
            db.create_verification_record(cust_id)
            
            # Initial Risk Score (Dummy for now, will be AI later)
            # In Phase B we just init logic, Phase C we connect it.
            # For now, we just create the record.
            
            db.log_action("Registration", "System", f"New customer registered: {cnic}")

            messagebox.showinfo("Success", "Application submitted successfully!")
            self.destroy()

        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Ensure DB is ready
    db.init_db()
    app = RegistrationApp()
    app.mainloop()
