import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from app import db, utils, security_utils

# Set Theme to Light for Fintech Vibe
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class FintechApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Fintech KYC & Banking")
        self.geometry("450x850") # Mobile-like aspect ratio
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.current_customer_id = None
        self.files = {}

        self.show_onboarding()

    def toggle_theme(self):
        mode = ctk.get_appearance_mode()
        new_mode = "Light" if mode == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)

    def clear_view(self):
        for widget in self.winfo_children():
            widget.destroy()

    # --- 1. Onboarding Screen (Active Login) ---
    def show_onboarding(self):
        self.clear_view()
        
        # Theme Toggle
        ctk.CTkButton(self, text="🌓", width=40, height=40, fg_color="transparent", text_color="gray", command=self.toggle_theme).place(x=350, y=10)
        
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True)
        
        # Logo
        ctk.CTkLabel(frame, text="🏦", font=("Arial", 60)).pack(pady=(60, 20))
        ctk.CTkLabel(frame, text="NeoBank", font=("Roboto", 32, "bold"), text_color="#2c3e50").pack(pady=10)
        ctk.CTkLabel(frame, text="Secure. Fast. Intelligent.", font=("Roboto", 16), text_color="gray").pack(pady=(0, 30))
        
        # Login Form
        self.login_cnic = ctk.CTkEntry(frame, placeholder_text="Enter CNIC (e.g. 42101...)", width=280, height=50, corner_radius=10)
        self.login_cnic.pack(pady=10)
        
        ctk.CTkButton(frame, text="Login to Dashboard", width=280, height=50, corner_radius=25, font=("Roboto", 16, "bold"), 
                    command=self.login_customer).pack(pady=10)
        
        ctk.CTkLabel(frame, text="OR", text_color="gray").pack(pady=10)
        
        ctk.CTkButton(frame, text="Open New Account", width=280, height=50, corner_radius=25, fg_color="transparent", border_width=2, text_color="#2c3e50", 
                    command=self.show_registration).pack(pady=10)

    def login_customer(self):
        cnic = self.login_cnic.get()
        if not cnic:
            messagebox.showwarning("Required", "Please enter your CNIC.")
            return
            
        # Check DB
        conn = db.get_conn()
        # Note: In real app, we decrypt CNIC to match, or hash it. 
        # For this demo, we will fetch all and match decrypted (slow but works for demo)
        # OR simpler: just check if ID exists for now since we encrypted everything
        # Let's use a simpler approach: If user exists, we let them in.
        
        # Fetch all customers
        customers = conn.execute("SELECT id, cnic FROM Customers").fetchall()
        conn.close()
        
        found_id = None
        for cust in customers:
            try:
                dec_cnic = security_utils.decrypt_data(cust['cnic'])
                if dec_cnic == cnic:
                    found_id = cust['id']
                    break
            except:
                continue
                
        if found_id:
            self.current_customer_id = found_id
            self.show_dashboard()
        else:
            messagebox.showerror("Login Failed", "No account found with this CNIC.\nPlease register first.")

    # --- 2. Registration Wizard (UX Overhaul) ---
    def show_registration(self):
        self.clear_view()
        self.files = {} # Reset files
        
        # Top Bar: Progress & Back
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(top_frame, text="← Back", fg_color="transparent", text_color="gray", width=50, command=self.show_onboarding).pack(side="left")
        ctk.CTkLabel(top_frame, text="Step 1 of 1: Application", font=("Roboto", 12, "bold"), text_color="#3498db").pack(side="right")
        
        # Main Scrollable Area
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=5)
        
        # Header
        ctk.CTkLabel(self.scroll, text="New Account Application", font=("Roboto", 22, "bold"), text_color="#2c3e50").pack(anchor="w", pady=(10, 5))
        ctk.CTkLabel(self.scroll, text="Please fill in your details accurately.", font=("Roboto", 12), text_color="gray").pack(anchor="w", pady=(0, 20))
        
        # AI Auto-Fill Button
        ai_frame = ctk.CTkFrame(self.scroll, fg_color="#e8f6f3", corner_radius=10)
        ai_frame.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(ai_frame, text="✨ Have your CNIC?", font=("Roboto", 12, "bold"), text_color="#16a085").pack(side="left", padx=15, pady=10)
        ctk.CTkButton(ai_frame, text="Auto-Fill with AI", width=120, height=30, fg_color="#1abc9c", hover_color="#16a085", command=self.auto_fill_data).pack(side="right", padx=15, pady=10)

        # --- SECTION 1: Personal Information ---
        self.create_section_header("👤 Personal Information")
        
        # Two-Column Grid
        grid_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        grid_frame.pack(fill="x", pady=5)
        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)
        
        self.entry_name = self.create_validated_input(grid_frame, "Full Legal Name", 0, 0)
        self.entry_cnic = self.create_validated_input(grid_frame, "CNIC (e.g. 42101...)", 0, 1)
        self.entry_email = self.create_validated_input(grid_frame, "Email Address", 1, 0)
        self.entry_phone = self.create_validated_input(grid_frame, "Phone Number", 1, 1)
        
        # Full Width Address
        self.entry_address = self.create_validated_input(self.scroll, "Home Address", None, None, full_width=True)
        
        # --- SECTION 2: Financials ---
        self.create_section_header("💰 Income Information")
        ctk.CTkLabel(self.scroll, text="Monthly Income Range", font=("Roboto", 12, "bold"), text_color="#34495e").pack(anchor="w", pady=(5, 2))
        self.combo_income = ctk.CTkComboBox(self.scroll, values=["Below 50k", "50k-100k", "100k-200k", "Above 200k"], height=40, border_color="#bdc3c7")
        self.combo_income.pack(fill="x", pady=5)

        # --- SECTION 3: Identity Verification ---
        self.create_section_header("🆔 Document Upload")
        
        self.preview_frames = {} # Store preview labels
        
        self.create_upload_row("Front of CNIC", "CNIC_Front")
        self.create_upload_row("Back of CNIC", "CNIC_Back")
        self.create_upload_row("Live Selfie", "Selfie")

        # Submit Area
        ctk.CTkButton(self.scroll, text="Review & Submit Application →", height=50, corner_radius=10, 
                    fg_color="#2980b9", font=("Roboto", 16, "bold"), hover_color="#3498db",
                    command=self.confirm_submission).pack(fill="x", pady=(30, 10))
                    
        # Trust Badge
        ctk.CTkLabel(self.scroll, text="🔒 Your data is AES-256 Encrypted & Secure.", font=("Arial", 10), text_color="gray").pack(pady=(0, 20))

    def create_section_header(self, text):
        ctk.CTkLabel(self.scroll, text=text, font=("Roboto", 14, "bold"), text_color="#2c3e50").pack(anchor="w", pady=(20, 10))
        ctk.CTkFrame(self.scroll, height=2, fg_color="#ecf0f1").pack(fill="x", pady=(0, 10))

    def create_validated_input(self, parent, placeholder, row, col, full_width=False):
        # Container for Label + Entry + Error Msg
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        if full_width:
            frame.pack(fill="x", pady=5)
        else:
            frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
        ctk.CTkLabel(frame, text=placeholder, font=("Roboto", 11, "bold"), text_color="#7f8c8d").pack(anchor="w")
        
        entry = ctk.CTkEntry(frame, placeholder_text=placeholder, height=40, corner_radius=8, border_color="#bdc3c7")
        entry.pack(fill="x", pady=(2, 0))
        
        # Validation Logic (Bind KeyRelease)
        entry.bind("<KeyRelease>", lambda event, e=entry, t=placeholder: self.validate_field(e, t))
        
        return entry

    def validate_field(self, entry, type_):
        val = entry.get()
        valid = True
        if "CNIC" in type_ and (len(val) < 13 or not val.replace("-","").isdigit()):
            valid = False
        elif "Phone" in type_ and (len(val) < 10 or not val.isdigit()):
            valid = False
            
        entry.configure(border_color="#e74c3c" if not valid else "#2ecc71")

    def create_upload_row(self, text, key):
        frame = ctk.CTkFrame(self.scroll, fg_color="white", corner_radius=10, border_width=1, border_color="#ecf0f1")
        frame.pack(pady=5, fill="x")
        
        # Icon & Text
        ctk.CTkLabel(frame, text="📄", font=("Arial", 20)).pack(side="left", padx=(15, 5), pady=15)
        ctk.CTkLabel(frame, text=text, font=("Roboto", 14)).pack(side="left", padx=5)
        
        # Preview Area (Hidden initially)
        preview_lbl = ctk.CTkLabel(frame, text="", width=0)
        preview_lbl.pack(side="right", padx=10)
        self.preview_frames[key] = preview_lbl
        
        btn = ctk.CTkButton(frame, text="Upload", width=80, height=30, corner_radius=15, fg_color="#ecf0f1", text_color="#2c3e50", hover_color="#bdc3c7",
                          command=lambda: self.upload_file(key, btn, preview_lbl))
        btn.pack(side="right", padx=10)

    def upload_file(self, key, btn, preview_lbl):
        # Allow common image formats
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if path:
            self.files[key] = path
            btn.configure(text="Change", fg_color="white", border_width=1, border_color="#bdc3c7")
            preview_lbl.configure(text="✅ Attached", text_color="#27ae60", width=80)

    def auto_fill_data(self):
        # Check if CNIC Front is uploaded
        if 'CNIC_Front' not in self.files:
            messagebox.showinfo("AI Assistant", "I need to see your ID card first! 📸\n\nPlease upload the 'Front of CNIC' image below, and I'll extract the details for you.")
            return
            
        # Simulate AI OCR
        from app import ai_utils
        data = ai_utils.simulate_ocr_extraction(self.files['CNIC_Front'])
        
        if data:
            self.entry_name.delete(0, "end"); self.entry_name.insert(0, data['name'])
            self.entry_cnic.delete(0, "end"); self.entry_cnic.insert(0, data['cnic'])
            
            messagebox.showinfo("AI OCR", "Details extracted from CNIC successfully!")
            self.validate_field(self.entry_cnic, "CNIC") # Trigger validation visual

    def confirm_submission(self):
        # Review Popup
        msg = f"""Please confirm your details:
        
Name: {self.entry_name.get()}
CNIC: {self.entry_cnic.get()}
Email: {self.entry_email.get()}
Phone: {self.entry_phone.get()}
Income: {self.combo_income.get()}

Documents: {len(self.files)} attached
"""
        if messagebox.askyesno("Confirm Submission", msg):
            self.submit_registration()

    def submit_registration(self):
        name = self.entry_name.get()
        cnic = self.entry_cnic.get()
        
        if not name or not cnic:
            messagebox.showerror("Error", "Name and CNIC are required.")
            return
            
        try:
            # Create Customer
            cust_id = db.insert_customer(name, cnic, self.entry_email.get(), self.entry_phone.get(), self.entry_address.get(), self.combo_income.get())
            self.current_customer_id = cust_id
            
            # Save Docs
            for k, v in self.files.items():
                if v: utils.save_uploaded_file(cust_id, v, k)
                
            # Init Verification & Financials
            db.create_verification_record(cust_id)
            db.generate_mock_financials(cust_id) 
            
            messagebox.showinfo("Success", "Application Submitted Successfully!\nRedirecting to Dashboard...")
            self.show_dashboard()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # --- 3. Banking Dashboard ---
    def show_dashboard(self):
        self.clear_view()
        
        # Fetch Data
        health, transactions = db.get_customer_financials(self.current_customer_id)
        cust = db.get_customer_by_id(self.current_customer_id)
        
        # Top Bar
        top = ctk.CTkFrame(self, height=60, fg_color="white", corner_radius=0)
        top.pack(fill="x")
        ctk.CTkLabel(top, text=f"Hi, {cust['full_name'].split()[0]}", font=("Roboto", 18, "bold")).pack(side="left", padx=20, pady=15)
        ctk.CTkLabel(top, text="🔔", font=("Arial", 20)).pack(side="right", padx=20)

        scroll = ctk.CTkScrollableFrame(self, fg_color="#f5f6fa")
        scroll.pack(fill="both", expand=True)

        # Balance Card
        card = ctk.CTkFrame(scroll, height=150, corner_radius=20, fg_color="#4834d4") # Blurple
        card.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(card, text="Total Balance", text_color="white", font=("Roboto", 12)).pack(anchor="w", padx=20, pady=(20,5))
        ctk.CTkLabel(card, text=f"PKR {health['predicted_balance']:,.0f}", text_color="white", font=("Roboto", 32, "bold")).pack(anchor="w", padx=20)
        
        # Financial Health
        health_frame = ctk.CTkFrame(scroll, fg_color="white", corner_radius=15)
        health_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(health_frame, text="Financial Health Score", font=("Roboto", 14, "bold")).pack(anchor="w", padx=15, pady=15)
        
        score = health['spending_score']
        
        # Dynamic Label & Color
        if score >= 80:
            grade = "Excellent"
            color = "#2ecc71" # Green
        elif score >= 60:
            grade = "Good"
            color = "#3498db" # Blue
        elif score >= 40:
            grade = "Fair"
            color = "#f1c40f" # Yellow
        else:
            grade = "Needs Improvement"
            color = "#e74c3c" # Red
            
        ctk.CTkProgressBar(health_frame, progress_color=color).pack(fill="x", padx=15, pady=(0,10))
        ctk.CTkLabel(health_frame, text=f"{score}/100 - {grade}", font=("Roboto", 12), text_color=color).pack(anchor="e", padx=15, pady=(0,15))

        # Transactions
        ctk.CTkLabel(scroll, text="Recent Transactions", font=("Roboto", 16, "bold"), text_color="#2c3e50").pack(anchor="w", padx=25, pady=10)
        
        if not transactions:
            ctk.CTkLabel(scroll, text="No recent transactions found.", font=("Roboto", 12), text_color="gray").pack(pady=10)
        else:
            for t in transactions:
                row = ctk.CTkFrame(scroll, fg_color="white", corner_radius=10)
                row.pack(fill="x", padx=20, pady=5)
                
                icon = "🍔" if t['category'] == "Food" else "🚗" if t['category'] == "Transport" else "💰"
                ctk.CTkLabel(row, text=icon, font=("Arial", 20)).pack(side="left", padx=15, pady=15)
                
                info = ctk.CTkFrame(row, fg_color="transparent")
                info.pack(side="left")
                ctk.CTkLabel(info, text=t['category'], font=("Roboto", 14, "bold")).pack(anchor="w")
                ctk.CTkLabel(info, text=t['date'].split()[0], font=("Arial", 10), text_color="gray").pack(anchor="w")
                
                amt_color = "#e74c3c" if t['type'] == "Debit" else "#2ecc71"
                sign = "-" if t['type'] == "Debit" else "+"
                ctk.CTkLabel(row, text=f"{sign}{t['amount']:,.0f}", font=("Roboto", 14, "bold"), text_color=amt_color).pack(side="right", padx=15)

if __name__ == "__main__":
    db.init_db()
    app = FintechApp()
    app.mainloop()
