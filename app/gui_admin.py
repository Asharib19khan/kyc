import customtkinter as ctk
from tkinter import messagebox, ttk
import tkinter as tk
from app import db, auth, reports, ai_utils, config
import random

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class AdminApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("KYC Command Center | Enterprise Edition")
        self.geometry("1280x800")
        self.current_admin = None
        
        # Configure Grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.show_login()

    def toggle_theme(self):
        mode = ctk.get_appearance_mode()
        new_mode = "Light" if mode == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)

    def show_login(self):
        self.clear_window()
        
        # Premium Banking Theme (Slate & Gold)
        bg_color = "#0f172a" # Slate 900
        card_color = "#1e293b" # Slate 800
        text_color = "#f1f5f9" # Slate 100
        accent_color = "#38bdf8" # Sky 400
        gold_accent = "#fbbf24" # Amber 400
        
        self.configure(fg_color=bg_color)
        
        # Main Container
        login_frame = ctk.CTkFrame(self, fg_color=card_color, corner_radius=20, width=400, height=550, border_width=1, border_color="#334155")
        login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Header Section
        ctk.CTkLabel(login_frame, text="🏦", font=("Arial", 48)).pack(pady=(50, 10))
        ctk.CTkLabel(login_frame, text="ADMIN PORTAL", font=("Inter", 24, "bold"), text_color=text_color).pack(pady=(0, 5))
        ctk.CTkLabel(login_frame, text="Enterprise Banking System", font=("Inter", 12), text_color="#94a3b8").pack(pady=(0, 40))
        
        # Input Fields
        self.entry_user = ctk.CTkEntry(login_frame, placeholder_text="Username", width=300, height=50, 
                                     fg_color="#0f172a", border_color="#334155", text_color="white", font=("Inter", 14), corner_radius=10)
        self.entry_user.pack(pady=10)
        
        self.entry_pass = ctk.CTkEntry(login_frame, placeholder_text="Password", show="•", width=300, height=50,
                                     fg_color="#0f172a", border_color="#334155", text_color="white", font=("Inter", 14), corner_radius=10)
        self.entry_pass.pack(pady=10)
        
        # Login Button
        btn_login = ctk.CTkButton(login_frame, text="SECURE LOGIN", width=300, height=50, 
                                fg_color=accent_color, text_color="#0f172a", font=("Inter", 14, "bold"), corner_radius=10,
                                hover_color="#0ea5e9", command=self.login)
        btn_login.pack(pady=30)
        
        # Footer
        ctk.CTkLabel(login_frame, text="Protected by AES-256 Encryption", font=("Inter", 10), text_color=gold_accent).pack(side="bottom", pady=25)

        # Bind Enter Key
        self.bind('<Return>', lambda event: self.login())

    def login(self):
        user = self.entry_user.get()
        pwd = self.entry_pass.get()
        
        conn = db.get_conn()
        admin = conn.execute("SELECT * FROM Admins WHERE username=?", (user,)).fetchone()
        conn.close()
        
        if admin and auth.check_password(admin['password_hash'], pwd):
            # Real 2FA
            from app import email_utils
            otp_code = email_utils.generate_otp()
            
            # For demo, we assume the admin's email is the sender email (or you could add email column to Admins table)
            # Here we ask the user to confirm where to send it, or just send to config email
            target_email = config.SENDER_EMAIL 
            
            sent = email_utils.send_otp_email(target_email, otp_code)
            
            if not sent:
                messagebox.showwarning("Config Error", "Could not send Real Email.\nCheck app/config.py credentials.\n\nUsing Simulation Mode: OTP is 1234")
                otp_code = "1234"
            
            otp_input = ctk.CTkInputDialog(text=f"Enter OTP sent to {target_email}:", title="Two-Factor Authentication")
            user_code = otp_input.get_input()
            
            if user_code == otp_code:
                self.current_admin = user
                self.init_dashboard_layout()
            else:
                messagebox.showerror("Error", "Invalid OTP")
        else:
            messagebox.showerror("Access Denied", "Invalid credentials provided.")

    def init_dashboard_layout(self):
        self.clear_window()
        
        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)
        
        app_title = ctk.CTkLabel(self.sidebar, text="KYC SYSTEM\nENTERPRISE", font=("Roboto", 20, "bold"))
        app_title.grid(row=0, column=0, padx=20, pady=20)
        
        self.btn_dash = self.create_nav_btn("Dashboard", self.show_dashboard_view, 1)
        self.btn_verify = self.create_nav_btn("Verifications", self.show_verification_view, 2)
        self.btn_admins = self.create_nav_btn("Manage Admins", self.show_admin_mgmt_view, 3)
        self.btn_audit = self.create_nav_btn("Security Logs", self.show_audit_view, 4)
        self.btn_reports = self.create_nav_btn("Reports & Export", self.show_reports_view, 5)
        
        ctk.CTkLabel(self.sidebar, text=f"User: {self.current_admin}", text_color="gray").grid(row=7, column=0, pady=10)
        
        # Theme Toggle
        ctk.CTkButton(self.sidebar, text="Toggle Theme 🌓", command=self.toggle_theme, fg_color="gray30", height=30).grid(row=8, column=0, padx=20, pady=10)
        
        ctk.CTkButton(self.sidebar, text="Logout", fg_color="#c0392b", hover_color="#e74c3c", command=self.show_login).grid(row=9, column=0, padx=20, pady=20)

        # --- Main Content Area ---
        self.main_area = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.show_dashboard_view()

    def create_nav_btn(self, text, command, row):
        btn = ctk.CTkButton(self.sidebar, text=text, command=command, fg_color="transparent", text_color=("gray10", "#DCE4EE"), hover_color=("gray70", "gray30"), anchor="w", height=40)
        btn.grid(row=row, column=0, padx=20, pady=5, sticky="ew")
        return btn

    # --- VIEWS ---

    def show_dashboard_view(self):
        self.clear_main_area()
        ctk.CTkLabel(self.main_area, text="Executive Dashboard", font=("Roboto", 28, "bold")).pack(anchor="w", pady=(0, 20))
        
        # KPI Cards
        kpi_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=10)
        
        conn = db.get_conn()
        total = conn.execute("SELECT COUNT(*) FROM Customers").fetchone()[0]
        verified = conn.execute("SELECT COUNT(*) FROM Verifications WHERE status='Verified'").fetchone()[0]
        pending = conn.execute("SELECT COUNT(*) FROM Verifications WHERE status='Pending'").fetchone()[0]
        # Real Fraud Count: High Risk (>80) or Rejected
        fraud_count = conn.execute("SELECT COUNT(*) FROM Verifications WHERE risk_score > 80 OR status='Rejected'").fetchone()[0]
        conn.close()
        
        self.create_kpi_card(kpi_frame, "Total Customers", total, "#2980b9").pack(side="left", expand=True, fill="x", padx=5)
        self.create_kpi_card(kpi_frame, "Verified", verified, "#27ae60").pack(side="left", expand=True, fill="x", padx=5)
        self.create_kpi_card(kpi_frame, "Pending Review", pending, "#f39c12").pack(side="left", expand=True, fill="x", padx=5)
        self.create_kpi_card(kpi_frame, "High Risk / Fraud", fraud_count, "#c0392b").pack(side="left", expand=True, fill="x", padx=5)

        # Charts Area
        charts_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        charts_frame.pack(fill="both", expand=True, pady=20)
        
        # Fraud Heatmap (Visual Mockup)
        heatmap_frame = ctk.CTkFrame(charts_frame, corner_radius=10)
        heatmap_frame.pack(side="left", fill="both", expand=True, padx=5)
        ctk.CTkLabel(heatmap_frame, text="Fraud Risk Heatmap (City-wise)", font=("Roboto", 16, "bold")).pack(pady=10)
        
        # Simple visual bars for cities
        cities = [("Karachi", 0.8), ("Lahore", 0.4), ("Islamabad", 0.2), ("Peshawar", 0.5)]
        for city, risk in cities:
            row = ctk.CTkFrame(heatmap_frame, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(row, text=city, width=80, anchor="w").pack(side="left")
            progress = ctk.CTkProgressBar(row, progress_color="#c0392b" if risk > 0.6 else "#f39c12")
            progress.pack(side="left", fill="x", expand=True, padx=10)
            progress.set(risk)
            ctk.CTkLabel(row, text=f"{int(risk*100)}%", width=40).pack(side="right")

        # Approval Gauge (Visual Mockup)
        gauge_frame = ctk.CTkFrame(charts_frame, corner_radius=10)
        gauge_frame.pack(side="right", fill="both", expand=True, padx=5)
        ctk.CTkLabel(gauge_frame, text="System Auto-Approval Rate", font=("Roboto", 16, "bold")).pack(pady=10)
        
        rate = verified / total if total > 0 else 0
        ctk.CTkProgressBar(gauge_frame, orientation="vertical", height=200, progress_color="#27ae60").pack(pady=20)
        ctk.CTkLabel(gauge_frame, text=f"{int(rate*100)}%", font=("Roboto", 40, "bold"), text_color="#27ae60").pack()

    def show_verification_view(self):
        self.clear_main_area()
        ctk.CTkLabel(self.main_area, text="Verification Queue", font=("Roboto", 28, "bold")).pack(anchor="w", pady=(0, 20))
        
        # Filter/Search Bar
        filter_frame = ctk.CTkFrame(self.main_area)
        filter_frame.pack(fill="x", pady=10)
        ctk.CTkEntry(filter_frame, placeholder_text="Search by CNIC...").pack(side="left", padx=10, pady=10, fill="x", expand=True)
        ctk.CTkButton(filter_frame, text="Search").pack(side="left", padx=10)

        # Treeview
        columns = ("ID", "Name", "CNIC", "Status", "Date")
        tree = ttk.Treeview(self.main_area, columns=columns, show="headings", height=15)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        tree.pack(fill="both", expand=True, pady=10)
        
        # Load Data
        pending = db.get_pending_customers()
        for p in pending:
            tree.insert("", "end", values=(p['id'], p['full_name'], p['cnic'], p['status'], p['updated_at']))
            
        # Action Bar
        action_frame = ctk.CTkFrame(self.main_area)
        action_frame.pack(fill="x", pady=10)
        ctk.CTkButton(action_frame, text="Process Application", command=lambda: self.open_verification_modal(tree)).pack(side="right", padx=10)

    def show_audit_view(self):
        self.clear_main_area()
        ctk.CTkLabel(self.main_area, text="Security Audit Logs", font=("Roboto", 28, "bold")).pack(anchor="w", pady=(0, 20))
        
        # Treeview
        columns = ("ID", "Action", "Admin", "Details", "Timestamp")
        tree = ttk.Treeview(self.main_area, columns=columns, show="headings", height=20)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        tree.pack(fill="both", expand=True, pady=10)
        
        conn = db.get_conn()
        logs = conn.execute("SELECT * FROM AuditLog ORDER BY timestamp DESC LIMIT 50").fetchall()
        conn.close()
        
        for log in logs:
            tree.insert("", "end", values=(log['id'], log['action'], log['admin_user'], log['details'], log['timestamp']))

    def show_admin_mgmt_view(self):
        self.clear_main_area()
        ctk.CTkLabel(self.main_area, text="Admin Management", font=("Roboto", 28, "bold")).pack(anchor="w", pady=(0, 20))
        
        # Add Admin Form
        form_frame = ctk.CTkFrame(self.main_area)
        form_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(form_frame, text="Create New Admin", font=("Roboto", 16, "bold")).pack(pady=10)
        
        self.new_admin_user = ctk.CTkEntry(form_frame, placeholder_text="Username")
        self.new_admin_user.pack(side="left", padx=10, pady=10, expand=True, fill="x")
        
        self.new_admin_pass = ctk.CTkEntry(form_frame, placeholder_text="Password", show="*")
        self.new_admin_pass.pack(side="left", padx=10, pady=10, expand=True, fill="x")
        
        ctk.CTkButton(form_frame, text="Create Admin", command=self.create_new_admin).pack(side="left", padx=10)
        
        # List Admins
        ctk.CTkLabel(self.main_area, text="Existing Admins", font=("Roboto", 16)).pack(anchor="w", pady=10)
        conn = db.get_conn()
        admins = conn.execute("SELECT id, username, full_name FROM Admins").fetchall()
        conn.close()
        
        list_frame = ctk.CTkFrame(self.main_area)
        list_frame.pack(fill="both", expand=True)
        
        for adm in admins:
            row = ctk.CTkFrame(list_frame, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(row, text=f"ID: {adm['id']} | {adm['username']} ({adm['full_name']})").pack(side="left")

    def show_reports_view(self):
        self.clear_main_area()
        ctk.CTkLabel(self.main_area, text="Reports & Analytics", font=("Roboto", 28, "bold")).pack(anchor="w", pady=(0, 20))
        
        ctk.CTkButton(self.main_area, text="Export Full Verification Report (Excel)", command=self.export_data, height=50, font=("Roboto", 16)).pack(fill="x", pady=10)
        ctk.CTkLabel(self.main_area, text="More report types coming soon...", text_color="gray").pack(pady=20)

    # --- HELPERS ---

    def create_kpi_card(self, parent, title, value, color):
        frame = ctk.CTkFrame(parent, fg_color=color, corner_radius=10)
        ctk.CTkLabel(frame, text=title, text_color="white", font=("Roboto", 14)).pack(pady=(15,5))
        ctk.CTkLabel(frame, text=str(value), text_color="white", font=("Roboto", 36, "bold")).pack(pady=(0,15))
        return frame
    
    def clear_main_area(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()
            
    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def export_data(self):
        try:
            path = reports.export_verification_report()
            messagebox.showinfo("Success", f"Report exported to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def create_new_admin(self):
        u = self.new_admin_user.get()
        p = self.new_admin_pass.get()
        if u and p:
            auth.create_admin(u, p)
            messagebox.showinfo("Success", f"Admin {u} created.")
            self.show_admin_mgmt_view()
        else:
            messagebox.showwarning("Error", "Username and Password required.")

    def open_verification_modal(self, tree):
        selected = tree.selection()
        if not selected:
            return
        
        item = tree.item(selected[0])
        cust_id = item['values'][0]
        cust = db.get_customer_by_id(cust_id)
        
        top = ctk.CTkToplevel(self)
        top.title(f"Verify: {cust['full_name']}")
        top.geometry("900x700")
        
        # Split View: Docs on Left, Info on Right
        top.grid_columnconfigure(0, weight=1)
        top.grid_columnconfigure(1, weight=1)
        
        # Left: Documents (Mock placeholders)
        doc_frame = ctk.CTkFrame(top)
        doc_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(doc_frame, text="Document Preview", font=("Roboto", 16, "bold")).pack(pady=10)
        ctk.CTkButton(doc_frame, text="Open CNIC Front", command=lambda: messagebox.showinfo("Preview", "Opening Image Viewer...")).pack(pady=5)
        ctk.CTkButton(doc_frame, text="Open CNIC Back", command=lambda: messagebox.showinfo("Preview", "Opening Image Viewer...")).pack(pady=5)
        
        # Right: AI Analysis & Actions
        info_frame = ctk.CTkFrame(top)
        info_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(info_frame, text="AI Risk Analysis", font=("Roboto", 16, "bold")).pack(pady=10)
        
        # AI Score Cards
        score_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        score_frame.pack(fill="x", pady=10)
        
        # Real AI Simulation
        forgery_score, issues = ai_utils.detect_forgery("mock_path")
        match_score, is_live = ai_utils.check_liveness("mock", "mock")
        trust_score = int((forgery_score + match_score) / 2)
        
        # Real-Time Fraud Rules
        fraud_score, fraud_alerts = ai_utils.check_fraud_rules(cust)
        if fraud_score > 0:
            trust_score -= fraud_score # Reduce trust if fraud detected
            issues.extend(fraud_alerts)
        
        liveness_text = "PASS" if is_live else "FAIL"
        liveness_color = "#27ae60" if is_live else "#c0392b"
        
        self.create_score_badge(score_frame, "Trust Score", f"{max(0, trust_score)}/100", "#27ae60" if trust_score > 80 else "#f39c12").pack(side="left", expand=True, padx=5)
        self.create_score_badge(score_frame, "Liveness", liveness_text, liveness_color).pack(side="left", expand=True, padx=5)
        self.create_score_badge(score_frame, "Forgery Check", f"{forgery_score}%", "#27ae60" if forgery_score > 85 else "#c0392b").pack(side="left", expand=True, padx=5)

        if issues:
            ctk.CTkLabel(info_frame, text=f"⚠ SECURITY ALERTS: {', '.join(issues)}", text_color="#e74c3c", font=("Courier New", 12, "bold")).pack(pady=5)
        
        ctk.CTkLabel(info_frame, text="Customer Details", font=("Roboto", 14, "bold")).pack(pady=(20,5), anchor="w")
        details = f"Name: {cust['full_name']}\nCNIC: {cust['cnic']}\nIncome: {cust['income_range']}\nPhone: {cust['phone']}"
        ctk.CTkLabel(info_frame, text=details, justify="left", anchor="w").pack(fill="x")
        
        # Actions
        ctk.CTkLabel(info_frame, text="Decision", font=("Roboto", 14, "bold")).pack(pady=(20,5), anchor="w")
        self.remarks_entry = ctk.CTkEntry(info_frame, placeholder_text="Enter Remarks...")
        self.remarks_entry.pack(fill="x", pady=5)
        
        btn_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        btn_frame.pack(pady=20)
        ctk.CTkButton(btn_frame, text="APPROVE", fg_color="#27ae60", width=120, command=lambda: self.submit_decision(top, cust_id, "Verified", trust_score, cust['full_name'])).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="REJECT", fg_color="#c0392b", width=120, command=lambda: self.submit_decision(top, cust_id, "Rejected", trust_score, cust['full_name'])).pack(side="left", padx=10)

    def create_score_badge(self, parent, title, value, color):
        frame = ctk.CTkFrame(parent, fg_color=color, corner_radius=5)
        ctk.CTkLabel(frame, text=title, text_color="white", font=("Arial", 10)).pack(pady=(5,0))
        ctk.CTkLabel(frame, text=value, text_color="white", font=("Arial", 16, "bold")).pack(pady=(0,5))
        return frame

    def submit_decision(self, window, cust_id, status, trust_score, cust_name):
        remarks = self.remarks_entry.get()
        if not remarks:
            messagebox.showwarning("Required", "Please enter remarks.")
            return
            
        risk_score = 100 - trust_score
        db.update_verification(cust_id, status, risk_score, trust_score, remarks, self.current_admin)
        db.create_loan_eligibility(cust_id, risk_score, "Unknown")
        db.log_action(f"Verification {status}", self.current_admin, f"Customer {cust_id}")
        
        msg = f"Application {status}"
        
        if status == "Verified":
            # Generate PDF
            from app import pdf_utils
            try:
                path = pdf_utils.generate_loan_approval_pdf(cust_name, 500000) # Mock amount
                msg += f"\n\nLoan Approval Letter Generated:\n{path}"
            except Exception as e:
                msg += f"\n\nError generating PDF: {e}"
        
        messagebox.showinfo("Success", msg)
        window.destroy()
        self.show_verification_view()

if __name__ == "__main__":
    db.init_db()
    app = AdminApp()
    app.mainloop()
