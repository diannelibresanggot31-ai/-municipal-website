import mysql.connector
from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime

class ModernMunicipalSystem:
    def __init__(self):
        self.db = None
        self.cursor = None
        self.current_user = None
        self.login_window()
    
    def connect_db(self):
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="dianne2005",
                database="municipal_db"
            )
            self.cursor = self.db.cursor(dictionary=True)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Database connection failed: {e}")
            return False
    
    def login_window(self):
        self.login_win = Tk()
        self.login_win.title("Municipal Information System")
        self.login_win.geometry("1000x600")
        self.login_win.configure(bg='#f4f4f4')
        
        # Center window
        self.login_win.eval('tk::PlaceWindow . center')
        
        # Main container
        main_frame = Frame(self.login_win, bg='#f4f4f4')
        main_frame.pack(fill='both', expand=True)
        
        # Left panel - Image/Info
        left_panel = Frame(main_frame, bg='#2c5f8a', width=400)
        left_panel.pack(side='left', fill='both', expand=True)
        
        # Logo/Icon
        logo_label = Label(left_panel, text="🏛️", font=('Segoe UI', 80), 
                          bg='#2c5f8a', fg='white')
        logo_label.pack(pady=50)
        
        # Welcome text
        welcome_text = """Municipal Government
Web-Based Information 
Management System

"Growing together, rooted 
in heritage and stability"

Empowering communities
through digital innovation"""
        
        Label(left_panel, text=welcome_text, font=('Segoe UI', 12), 
              bg='#2c5f8a', fg='white', justify='left').pack(pady=20)
        
        # Right panel - Login Form
        right_panel = Frame(main_frame, bg='white', width=600)
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Login form container
        form_frame = Frame(right_panel, bg='white')
        form_frame.pack(expand=True, pady=80)
        
        Label(form_frame, text="Welcome Back", font=('Segoe UI', 24, 'bold'),
              bg='white', fg='#2c5f8a').pack(pady=10)
        
        Label(form_frame, text="Sign in to access municipal services", 
              font=('Segoe UI', 10), bg='white', fg='#666').pack(pady=5)
        
        # Username
        Label(form_frame, text="Username", font=('Segoe UI', 10), 
              bg='white', fg='#333', anchor='w').pack(fill='x', pady=(20,5))
        self.username_entry = Entry(form_frame, font=('Segoe UI', 12), 
                                    bg='#f8f9fa', relief='flat', bd=1)
        self.username_entry.pack(fill='x', pady=5, ipady=8)
        
        # Password
        Label(form_frame, text="Password", font=('Segoe UI', 10), 
              bg='white', fg='#333', anchor='w').pack(fill='x', pady=(10,5))
        self.password_entry = Entry(form_frame, show="*", font=('Segoe UI', 12),
                                    bg='#f8f9fa', relief='flat', bd=1)
        self.password_entry.pack(fill='x', pady=5, ipady=8)
        
        # Login button
        login_btn = Button(form_frame, text="Sign In", command=self.login,
                          bg='#2c5f8a', fg='white', font=('Segoe UI', 12, 'bold'),
                          relief='flat', cursor='hand2')
        login_btn.pack(fill='x', pady=30, ipady=10)
        
        self.login_win.mainloop()
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showwarning("Warning", "Please enter username and password")
            return
        
        if self.connect_db():
            self.cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", 
                              (username, password))
            user = self.cursor.fetchone()
            self.db.close()
            
            if user:
                self.current_user = user
                self.login_win.destroy()
                if user['role'] == 'admin':
                    self.admin_dashboard()
                else:
                    self.user_dashboard()
            else:
                messagebox.showerror("Error", "Invalid username or password!")
    
    def user_dashboard(self):
        user_win = Tk()
        user_win.title("Municipal Information System - Citizen Portal")
        user_win.geometry("1200x700")
        user_win.configure(bg='#f4f4f4')
        
        # Header
        header = Frame(user_win, bg='#2c5f8a', height=100)
        header.pack(fill='x')
        
        title_frame = Frame(header, bg='#2c5f8a')
        title_frame.pack(pady=20)
        
        Label(title_frame, text="🏛️", font=('Segoe UI', 40), 
              bg='#2c5f8a').pack(side='left')
        
        Label(title_frame, text="Municipal Government Information System", 
              font=('Segoe UI', 18, 'bold'), bg='#2c5f8a', fg='white',
              justify='left').pack(side='left', padx=15)
        
        Label(header, text="Growing together, rooted in heritage and stability", 
              font=('Segoe UI', 10, 'italic'), bg='#2c5f8a', fg='#c8e7f5').pack()
        
        # User info bar
        info_bar = Frame(user_win, bg='#1a4668', height=40)
        info_bar.pack(fill='x')
        
        Label(info_bar, text=f"Welcome, {self.current_user['full_name']}", 
              bg='#1a4668', fg='white', font=('Segoe UI', 10)).pack(side='left', padx=20, pady=8)
        
        Button(info_bar, text="Logout", command=lambda: [user_win.destroy(), self.login_window()],
               bg='#e74c3c', fg='white', font=('Segoe UI', 9, 'bold'),
               relief='flat').pack(side='right', padx=20, pady=4)
        
        # Tab Control
        tab_control = ttk.Notebook(user_win)
        tab_control.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create tabs
        announcements_tab = Frame(tab_control, bg='#f4f4f4')
        inquiry_tab = Frame(tab_control, bg='#f4f4f4')
        
        tab_control.add(announcements_tab, text='📢 News & Announcements')
        tab_control.add(inquiry_tab, text='✉️ Submit Inquiry')
        
        # Populate tabs
        self.user_announcements_tab(announcements_tab)
        self.user_inquiry_tab(inquiry_tab)
        
        user_win.mainloop()
    
    def user_announcements_tab(self, parent):
        # Canvas with scrollbar
        canvas = Canvas(parent, bg='#f4f4f4', highlightthickness=0)
        scrollbar = Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas, bg='#f4f4f4')
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def load_announcements():
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            
            self.connect_db()
            self.cursor.execute("SELECT * FROM announcements ORDER BY date_posted DESC")
            announcements = self.cursor.fetchall()
            self.db.close()
            
            for ann in announcements:
                # Card frame
                card = Frame(scrollable_frame, bg='white', relief='flat', bd=1)
                card.pack(fill='x', padx=20, pady=10, ipady=10)
                
                # Title
                title_label = Label(card, text=f"📢 {ann['title']}", 
                                   font=('Segoe UI', 14, 'bold'), 
                                   bg='white', fg='#2c5f8a', anchor='w')
                title_label.pack(fill='x', padx=15, pady=(10,5))
                
                # Date
                date_str = ann['date_posted'].strftime("%B %d, %Y at %I:%M %p") if hasattr(ann['date_posted'], 'strftime') else str(ann['date_posted'])
                Label(card, text=f"Posted: {date_str}", font=('Segoe UI', 9),
                      bg='white', fg='#999').pack(anchor='w', padx=15)
                
                # Content
                Label(card, text=ann['content'], font=('Segoe UI', 10),
                      bg='white', fg='#444', wraplength=800, justify='left',
                      anchor='w').pack(anchor='w', padx=15, pady=10)
                
                # Separator
                Frame(card, bg='#e0e0e0', height=1).pack(fill='x', padx=15, pady=10)
        
        refresh_btn = Button(parent, text="⟳ Refresh Announcements", 
                            command=load_announcements,
                            bg='#2c5f8a', fg='white', font=('Segoe UI', 10, 'bold'),
                            relief='flat')
        refresh_btn.pack(pady=10)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        load_announcements()
    
    def user_inquiry_tab(self, parent):
        # Form container
        form_container = Frame(parent, bg='#f4f4f4')
        form_container.pack(expand=True, fill='both', padx=100, pady=50)
        
        # Form card
        form_card = Frame(form_container, bg='white', relief='flat', bd=1)
        form_card.pack(fill='both', expand=True, padx=30, pady=30)
        
        Label(form_card, text="✉️ Submit an Inquiry", 
              font=('Segoe UI', 20, 'bold'), bg='white', fg='#2c5f8a').pack(pady=20)
        
        Label(form_card, text="Have questions? Send us a message and we'll respond promptly.", 
              font=('Segoe UI', 10), bg='white', fg='#666').pack(pady=(0,20))
        
        # Form fields
        fields_frame = Frame(form_card, bg='white')
        fields_frame.pack(padx=50, pady=20, fill='both')
        
        # Name
        Label(fields_frame, text="Full Name *", font=('Segoe UI', 10, 'bold'),
              bg='white', anchor='w').pack(fill='x')
        name_entry = Entry(fields_frame, font=('Segoe UI', 11), bg='#f8f9fa',
                          relief='flat', bd=1)
        name_entry.pack(fill='x', pady=(5,15), ipady=8)
        name_entry.insert(0, self.current_user['full_name'])
        
        # Email
        Label(fields_frame, text="Email", font=('Segoe UI', 10, 'bold'),
              bg='white', anchor='w').pack(fill='x')
        email_entry = Entry(fields_frame, font=('Segoe UI', 11), bg='#f8f9fa',
                           relief='flat', bd=1)
        email_entry.pack(fill='x', pady=(5,15), ipady=8)
        
        # Message
        Label(fields_frame, text="Message *", font=('Segoe UI', 10, 'bold'),
              bg='white', anchor='w').pack(fill='x')
        message_text = Text(fields_frame, font=('Segoe UI', 11), bg='#f8f9fa',
                           height=6, relief='flat', bd=1)
        message_text.pack(fill='x', pady=(5,20))
        
        def submit():
            name = name_entry.get()
            email = email_entry.get()
            message = message_text.get("1.0", END).strip()
            
            if name and message:
                self.connect_db()
                self.cursor.execute("INSERT INTO inquiries (name, email, message) VALUES (%s, %s, %s)",
                                  (name, email, message))
                self.db.commit()
                self.db.close()
                messagebox.showinfo("Success", "Inquiry submitted successfully!")
                message_text.delete("1.0", END)
            else:
                messagebox.showwarning("Warning", "Please fill in name and message")
        
        submit_btn = Button(fields_frame, text="Submit Inquiry", command=submit,
                           bg='#27ae60', fg='white', font=('Segoe UI', 12, 'bold'),
                           relief='flat')
        submit_btn.pack(pady=10, ipady=10)
    
    def admin_dashboard(self):
        admin_win = Tk()
        admin_win.title("Municipal System - Admin Dashboard")
        admin_win.geometry("1200x700")
        admin_win.configure(bg='#f4f4f4')
        
        # Header
        header = Frame(admin_win, bg='#2c5f8a', height=100)
        header.pack(fill='x')
        
        title_frame = Frame(header, bg='#2c5f8a')
        title_frame.pack(pady=20)
        
        Label(title_frame, text="🏛️", font=('Segoe UI', 40), 
              bg='#2c5f8a').pack(side='left')
        
        Label(title_frame, text="Admin Control Panel", 
              font=('Segoe UI', 18, 'bold'), bg='#2c5f8a', fg='white').pack(side='left', padx=15)
        
        info_bar = Frame(admin_win, bg='#1a4668', height=40)
        info_bar.pack(fill='x')
        
        Label(info_bar, text=f"Welcome, {self.current_user['full_name']} (Administrator)", 
              bg='#1a4668', fg='white', font=('Segoe UI', 10)).pack(side='left', padx=20, pady=8)
        
        Button(info_bar, text="Logout", command=lambda: [admin_win.destroy(), self.login_window()],
               bg='#e74c3c', fg='white', font=('Segoe UI', 9, 'bold'),
               relief='flat').pack(side='right', padx=20, pady=4)
        
        # Tab Control
        tab_control = ttk.Notebook(admin_win)
        tab_control.pack(fill='both', expand=True, padx=20, pady=20)
        
        dashboard_tab = Frame(tab_control)
        announcements_tab = Frame(tab_control)
        inquiries_tab = Frame(tab_control)
        
        tab_control.add(dashboard_tab, text='📊 Dashboard')
        tab_control.add(announcements_tab, text='📢 Announcements')
        tab_control.add(inquiries_tab, text='📝 Inquiries')
        
        self.admin_dashboard_tab(dashboard_tab)
        self.admin_announcements_tab(announcements_tab)
        self.admin_inquiries_tab(inquiries_tab)
        
        admin_win.mainloop()
    
    def admin_dashboard_tab(self, parent):
        self.connect_db()
        
        self.cursor.execute("SELECT COUNT(*) as count FROM announcements")
        ann_count = self.cursor.fetchone()['count']
        
        self.cursor.execute("SELECT COUNT(*) as count FROM inquiries WHERE status='pending'")
        pending_count = self.cursor.fetchone()['count']
        
        self.cursor.execute("SELECT COUNT(*) as count FROM users")
        users_count = self.cursor.fetchone()['count']
        
        self.db.close()
        
        stats_frame = Frame(parent, bg='#f4f4f4')
        stats_frame.pack(expand=True, fill='both', padx=50, pady=50)
        
        stats = [
            ("📢 Total Announcements", ann_count, "#3498db"),
            ("📝 Pending Inquiries", pending_count, "#e74c3c"),
            ("👥 Total Users", users_count, "#27ae60")
        ]
        
        for i, (title, value, color) in enumerate(stats):
            card = Frame(stats_frame, bg='white', relief='flat', bd=1)
            card.grid(row=0, column=i, padx=20, pady=20, ipadx=30, ipady=30, sticky='nsew')
            
            Label(card, text=title, font=('Segoe UI', 12, 'bold'),
                  bg='white', fg=color).pack()
            Label(card, text=str(value), font=('Segoe UI', 36, 'bold'),
                  bg='white', fg=color).pack(pady=10)
        
        stats_frame.grid_columnconfigure(list(range(3)), weight=1)
    
    def admin_announcements_tab(self, parent):
        add_frame = LabelFrame(parent, text="Post New Announcement", 
                               font=('Segoe UI', 12, 'bold'), padx=20, pady=20)
        add_frame.pack(fill='x', padx=20, pady=10)
        
        Label(add_frame, text="Title:", font=('Segoe UI', 10)).grid(row=0, column=0, sticky='w', pady=5)
        title_entry = Entry(add_frame, width=70, font=('Segoe UI', 11))
        title_entry.grid(row=0, column=1, pady=5, padx=10)
        
        Label(add_frame, text="Content:", font=('Segoe UI', 10)).grid(row=1, column=0, sticky='w', pady=5)
        content_text = Text(add_frame, height=6, width=70, font=('Segoe UI', 11))
        content_text.grid(row=1, column=1, pady=5, padx=10)
        
        def add_announcement():
            title = title_entry.get()
            content = content_text.get("1.0", END).strip()
            
            if title and content:
                self.connect_db()
                self.cursor.execute("INSERT INTO announcements (title, content, posted_by) VALUES (%s, %s, %s)",
                                  (title, content, self.current_user['username']))
                self.db.commit()
                self.db.close()
                messagebox.showinfo("Success", "Announcement posted!")
                title_entry.delete(0, END)
                content_text.delete("1.0", END)
            else:
                messagebox.showwarning("Warning", "Please enter title and content")
        
        Button(add_frame, text="Publish Announcement", command=add_announcement,
               bg='#27ae60', fg='white', font=('Segoe UI', 10, 'bold'),
               relief='flat').grid(row=2, column=0, columnspan=2, pady=10)
    
    def admin_inquiries_tab(self, parent):
        inquiry_frame = Frame(parent, bg='#f4f4f4')
        inquiry_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('ID', 'Name', 'Email', 'Message', 'Status', 'Date')
        tree = ttk.Treeview(inquiry_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        tree.column('Message', width=300)
        
        scrollbar = Scrollbar(inquiry_frame, orient=VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=LEFT, fill='both', expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        def refresh():
            for item in tree.get_children():
                tree.delete(item)
            
            self.connect_db()
            self.cursor.execute("SELECT * FROM inquiries ORDER BY date_submitted DESC")
            for inquiry in self.cursor.fetchall():
                msg = inquiry['message'][:50] + "..." if len(inquiry['message']) > 50 else inquiry['message']
                tree.insert('', END, values=(
                    inquiry['id'],
                    inquiry['name'],
                    inquiry['email'],
                    msg,
                    inquiry['status'],
                    inquiry['date_submitted']
                ))
            self.db.close()
        
        Button(inquiry_frame, text="Refresh", command=refresh,
               bg='#3498db', fg='white', font=('Segoe UI', 10, 'bold')).pack(pady=5)
        
        refresh()

# Run the application
if __name__ == "__main__":
    app = ModernMunicipalSystem()