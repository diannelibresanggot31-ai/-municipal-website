import mysql.connector
from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime
import webbrowser

class PublicMunicipalWebsite:
    def __init__(self):
        self.db = None
        self.cursor = None
        self.main_window()
    
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
            print(f"Database error: {e}")
            return False
    
    def main_window(self):
        self.window = Tk()
        self.window.title("Municipal Government - Official Website")
        self.window.geometry("1300x800")
        self.window.configure(bg='#f5f5f0')
        
        # Create scrollable main frame
        main_canvas = Canvas(self.window, bg='#f5f5f0', highlightthickness=0)
        scrollbar = Scrollbar(self.window, orient="vertical", command=main_canvas.yview)
        scrollable_frame = Frame(main_canvas, bg='#f5f5f0')
        
        scrollable_frame.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Build the website
        self.create_header(scrollable_frame)
        self.create_hero_section(scrollable_frame)
        self.create_quick_links(scrollable_frame)
        self.create_announcements_section(scrollable_frame)
        self.create_services_section(scrollable_frame)
        self.create_inquiry_section(scrollable_frame)
        self.create_footer(scrollable_frame)
        
        self.window.mainloop()
    
    def create_header(self, parent):
        # Top bar
        top_bar = Frame(parent, bg='#1a3c5e', height=40)
        top_bar.pack(fill='x')
        
        Label(top_bar, text="📞 (555) 123-4567", bg='#1a3c5e', fg='white', 
              font=('Segoe UI', 9)).pack(side='left', padx=20, pady=8)
        Label(top_bar, text="📍 123 Municipal Hall, City Center", bg='#1a3c5e', fg='white',
              font=('Segoe UI', 9)).pack(side='right', padx=20, pady=8)
        
        # Main header
        header = Frame(parent, bg='white', height=100)
        header.pack(fill='x')
        
        # Logo and title
        logo_frame = Frame(header, bg='white')
        logo_frame.pack(side='left', padx=50, pady=20)
        
        Label(logo_frame, text="🏛️", font=('Segoe UI', 48), bg='white').pack(side='left')
        
        title_frame = Frame(logo_frame, bg='white')
        title_frame.pack(side='left', padx=15)
        
        Label(title_frame, text="Municipality of", font=('Segoe UI', 12), 
              bg='white', fg='#666').pack(anchor='w')
        Label(title_frame, text="San Francisco", font=('Segoe UI', 24, 'bold'), 
              bg='white', fg='#1a3c5e').pack(anchor='w')
        
        # Navigation menu
        nav_frame = Frame(header, bg='white')
        nav_frame.pack(side='right', padx=50)
        
        nav_items = ["Home", "Announcements", "Services", "Barangays", "Contact"]
        for item in nav_items:
            btn = Label(nav_frame, text=item, font=('Segoe UI', 11), 
                       bg='white', fg='#333', cursor='hand2')
            btn.pack(side='left', padx=15, pady=30)
        
        # Tagline bar
        tagline = Frame(parent, bg='#e8f0f8', height=50)
        tagline.pack(fill='x')
        
        Label(tagline, text="🌱 Growing together, rooted in heritage and stability", 
              font=('Segoe UI', 11, 'italic'), bg='#e8f0f8', fg='#1a3c5e').pack(pady=12)
    
    def create_hero_section(self, parent):
        hero = Frame(parent, bg='#1a3c5e', height=400)
        hero.pack(fill='x')
        
        # Hero content
        hero_content = Frame(hero, bg='#1a3c5e')
        hero_content.pack(expand=True, pady=80)
        
        Label(hero_content, text="Welcome to Our Municipality", 
              font=('Segoe UI', 36, 'bold'), bg='#1a3c5e', fg='white').pack()
        
        Label(hero_content, text="Building a better tomorrow, together", 
              font=('Segoe UI', 16), bg='#1a3c5e', fg='#c8e7f5').pack(pady=10)
        
        # Search bar
        search_frame = Frame(hero_content, bg='white', relief='flat', bd=0)
        search_frame.pack(pady=30)
        
        search_entry = Entry(search_frame, font=('Segoe UI', 12), width=50,
                            bg='white', fg='#333', relief='flat')
        search_entry.pack(side='left', padx=0, ipady=10)
        search_entry.insert(0, "Search services, announcements...")
        
        search_btn = Button(search_frame, text="🔍 Search", 
                           bg='#f0a500', fg='white', font=('Segoe UI', 11, 'bold'),
                           relief='flat', cursor='hand2')
        search_btn.pack(side='left', padx=5, ipadx=20, ipady=8)
    
    def create_quick_links(self, parent):
        links_frame = Frame(parent, bg='white', pady=30)
        links_frame.pack(fill='x', padx=50, pady=20)
        
        Label(links_frame, text="Quick Links", font=('Segoe UI', 20, 'bold'),
              bg='white', fg='#1a3c5e').pack(pady=20)
        
        links = [
            ("📄 Park Rental", "Reserve parks and facilities"),
            ("👥 Residents", "Information for residents"),
            ("🏛️ Village Board", "Meet your officials"),
            ("📋 Agendas & Minutes", "Meeting documents"),
            ("📜 Ordinances", "Local laws and codes")
        ]
        
        links_container = Frame(links_frame, bg='white')
        links_container.pack()
        
        for i, (title, desc) in enumerate(links):
            card = Frame(links_container, bg='#f8f9fa', relief='ridge', bd=1)
            card.grid(row=0, column=i, padx=10, pady=10, ipadx=20, ipady=15)
            
            Label(card, text=title, font=('Segoe UI', 12, 'bold'),
                  bg='#f8f9fa', fg='#1a3c5e').pack()
            Label(card, text=desc, font=('Segoe UI', 9),
                  bg='#f8f9fa', fg='#666').pack(pady=5)
        
        links_container.grid_columnconfigure(list(range(5)), weight=1)
    
    def create_announcements_section(self, parent):
        # Section header
        header_frame = Frame(parent, bg='#f5f5f0')
        header_frame.pack(fill='x', padx=50, pady=(30, 10))
        
        Label(header_frame, text="📢 News & Announcements", 
              font=('Segoe UI', 24, 'bold'), bg='#f5f5f0', fg='#1a3c5e').pack(side='left')
        
        view_all = Label(header_frame, text="View All →", font=('Segoe UI', 11),
                        bg='#f5f5f0', fg='#f0a500', cursor='hand2')
        view_all.pack(side='right')
        
        # Announcements container
        announcements_frame = Frame(parent, bg='#f5f5f0')
        announcements_frame.pack(fill='both', expand=True, padx=50, pady=10)
        
        self.connect_db()
        self.cursor.execute("SELECT * FROM announcements ORDER BY date_posted DESC LIMIT 3")
        announcements = self.cursor.fetchall()
        
        for i, ann in enumerate(announcements):
            # Card
            card = Frame(announcements_frame, bg='white', relief='ridge', bd=1)
            card.pack(fill='x', pady=10, ipady=10)
            
            # Title
            title_frame = Frame(card, bg='white')
            title_frame.pack(fill='x', padx=20, pady=10)
            
            Label(title_frame, text="📢", font=('Segoe UI', 16), 
                  bg='white').pack(side='left')
            
            Label(title_frame, text=ann['title'], font=('Segoe UI', 14, 'bold'),
                  bg='white', fg='#1a3c5e').pack(side='left', padx=10)
            
            # Date
            date_str = ann['date_posted'].strftime("%B %d, %Y") if hasattr(ann['date_posted'], 'strftime') else str(ann['date_posted'])
            Label(card, text=f"📅 {date_str}", font=('Segoe UI', 9),
                  bg='white', fg='#999').pack(anchor='w', padx=50)
            
            # Content preview
            content_preview = ann['content'][:200] + "..." if len(ann['content']) > 200 else ann['content']
            Label(card, text=content_preview, font=('Segoe UI', 10),
                  bg='white', fg='#444', wraplength=900, justify='left',
                  anchor='w').pack(anchor='w', padx=50, pady=5)
            
            # Read more button
            read_more = Label(card, text="Read More →", font=('Segoe UI', 9, 'bold'),
                             bg='white', fg='#f0a500', cursor='hand2')
            read_more.pack(anchor='w', padx=50, pady=(0, 10))
        
        self.db.close()
    
    def create_services_section(self, parent):
        # Section header
        header_frame = Frame(parent, bg='#f5f5f0')
        header_frame.pack(fill='x', padx=50, pady=(40, 20))
        
        Label(header_frame, text="🛠️ Municipal Services", 
              font=('Segoe UI', 24, 'bold'), bg='#f5f5f0', fg='#1a3c5e').pack(side='left')
        
        # Services grid
        services_frame = Frame(parent, bg='#f5f5f0')
        services_frame.pack(fill='x', padx=50, pady=10)
        
        services = [
            ("📄 Business Permits", "Apply for new business permits or renew existing ones", "#e8f0f8"),
            ("🏠 Building Permits", "Get permits for construction and renovations", "#f8f9fa"),
            ("🗳️ Civil Registry", "Birth, marriage, and death certificates", "#e8f0f8"),
            ("💰 Tax Payments", "Pay your property and business taxes online", "#f8f9fa"),
            ("🗑️ Waste Management", "Schedule garbage collection and recycling", "#e8f0f8"),
            ("🌳 Parks & Recreation", "Book parks and recreational facilities", "#f8f9fa")
        ]
        
        for i, (title, desc, color) in enumerate(services):
            row = i // 3
            col = i % 3
            
            card = Frame(services_frame, bg=color, relief='ridge', bd=1)
            card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew', ipadx=10, ipady=15)
            
            Label(card, text=title, font=('Segoe UI', 12, 'bold'),
                  bg=color, fg='#1a3c5e').pack(anchor='w', padx=15, pady=(10,5))
            Label(card, text=desc, font=('Segoe UI', 9),
                  bg=color, fg='#666', wraplength=300, justify='left',
                  anchor='w').pack(anchor='w', padx=15, pady=(0,10))
            
            learn_btn = Label(card, text="Learn More →", font=('Segoe UI', 9, 'bold'),
                             bg=color, fg='#f0a500', cursor='hand2')
            learn_btn.pack(anchor='w', padx=15, pady=(0,10))
        
        services_frame.grid_columnconfigure(list(range(3)), weight=1)
    
    def create_inquiry_section(self, parent):
        # Contact form section
        contact_frame = Frame(parent, bg='#1a3c5e')
        contact_frame.pack(fill='x', padx=50, pady=40, ipady=30)
        
        left_col = Frame(contact_frame, bg='#1a3c5e')
        left_col.pack(side='left', padx=50, expand=True)
        
        Label(left_col, text="Have Questions?", font=('Segoe UI', 28, 'bold'),
              bg='#1a3c5e', fg='white').pack(anchor='w')
        Label(left_col, text="Send us a message and we'll respond within 24 hours", 
              font=('Segoe UI', 11), bg='#1a3c5e', fg='#c8e7f5').pack(anchor='w', pady=10)
        
        # Quick contact info
        contact_info = [
            ("📞 Phone", "(555) 123-4567"),
            ("✉️ Email", "info@municipality.gov"),
            ("📍 Address", "123 Municipal Hall, City Center")
        ]
        
        for label, value in contact_info:
            info_frame = Frame(left_col, bg='#1a3c5e')
            info_frame.pack(anchor='w', pady=10)
            Label(info_frame, text=label + ":", font=('Segoe UI', 10, 'bold'),
                  bg='#1a3c5e', fg='#f0a500').pack(side='left')
            Label(info_frame, text=value, font=('Segoe UI', 10),
                  bg='#1a3c5e', fg='white').pack(side='left', padx=10)
        
        right_col = Frame(contact_frame, bg='#1a3c5e')
        right_col.pack(side='right', padx=50, expand=True)
        
        # Simple inquiry form
        Label(right_col, text="Send Quick Message", font=('Segoe UI', 16, 'bold'),
              bg='#1a3c5e', fg='white').pack(anchor='w')
        
        name_entry = Entry(right_col, font=('Segoe UI', 11), bg='white', 
                          relief='flat', width=40)
        name_entry.pack(pady=5, ipady=8)
        name_entry.insert(0, "Your Name")
        
        email_entry = Entry(right_col, font=('Segoe UI', 11), bg='white',
                           relief='flat', width=40)
        email_entry.pack(pady=5, ipady=8)
        email_entry.insert(0, "Your Email")
        
        msg_text = Text(right_col, font=('Segoe UI', 11), bg='white',
                       height=4, width=40, relief='flat')
        msg_text.pack(pady=5)
        msg_text.insert("1.0", "Your Message")
        
        def submit_inquiry():
            name = name_entry.get()
            email = email_entry.get()
            message = msg_text.get("1.0", END).strip()
            
            if name and message and name != "Your Name":
                self.connect_db()
                self.cursor.execute("INSERT INTO inquiries (name, email, message) VALUES (%s, %s, %s)",
                                  (name, email, message))
                self.db.commit()
                self.db.close()
                messagebox.showinfo("Success", "Message sent successfully!")
                name_entry.delete(0, END)
                email_entry.delete(0, END)
                msg_text.delete("1.0", END)
                name_entry.insert(0, "Your Name")
                email_entry.insert(0, "Your Email")
                msg_text.insert("1.0", "Your Message")
            else:
                messagebox.showwarning("Warning", "Please enter your name and message")
        
        send_btn = Button(right_col, text="Send Message →", command=submit_inquiry,
                         bg='#f0a500', fg='white', font=('Segoe UI', 11, 'bold'),
                         relief='flat', cursor='hand2')
        send_btn.pack(pady=10, ipadx=20, ipady=8)
    
    def create_footer(self, parent):
        footer = Frame(parent, bg='#0d2137', height=150)
        footer.pack(fill='x')
        
        footer_content = Frame(footer, bg='#0d2137')
        footer_content.pack(pady=30)
        
        # Footer columns
        col1 = Frame(footer_content, bg='#0d2137')
        col1.pack(side='left', padx=50)
        
        Label(col1, text="🏛️ Municipality", font=('Segoe UI', 14, 'bold'),
              bg='#0d2137', fg='white').pack(anchor='w')
        Label(col1, text="Building a better tomorrow, together", 
              font=('Segoe UI', 9), bg='#0d2137', fg='#888').pack(anchor='w', pady=5)
        
        col2 = Frame(footer_content, bg='#0d2137')
        col2.pack(side='left', padx=50)
        
        Label(col2, text="Quick Links", font=('Segoe UI', 12, 'bold'),
              bg='#0d2137', fg='white').pack(anchor='w')
        for link in ["Home", "Announcements", "Services", "Contact"]:
            Label(col2, text=link, font=('Segoe UI', 9), bg='#0d2137', 
                  fg='#888', cursor='hand2').pack(anchor='w', pady=2)
        
        col3 = Frame(footer_content, bg='#0d2137')
        col3.pack(side='left', padx=50)
        
        Label(col3, text="Connect With Us", font=('Segoe UI', 12, 'bold'),
              bg='#0d2137', fg='white').pack(anchor='w')
        Label(col3, text="Facebook", font=('Segoe UI', 9), bg='#0d2137', 
              fg='#888', cursor='hand2').pack(anchor='w', pady=2)
        Label(col3, text="Twitter", font=('Segoe UI', 9), bg='#0d2137',
              fg='#888', cursor='hand2').pack(anchor='w', pady=2)
        
        # Copyright
        copyright_frame = Frame(footer, bg='#07101f', height=40)
        copyright_frame.pack(fill='x', side='bottom')
        
        Label(copyright_frame, text="© 2026 Municipality. All rights reserved.", 
              font=('Segoe UI', 9), bg='#07101f', fg='#666').pack(pady=10)

# Run the website
if __name__ == "__main__":
    app = PublicMunicipalWebsite()