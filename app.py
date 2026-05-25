from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
from datetime import datetime
from functools import wraps
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'municipal_secret_key_2026')

# ── Register templates_admin as additional template folder ──
from jinja2 import ChoiceLoader, FileSystemLoader
app.jinja_loader = ChoiceLoader([
    FileSystemLoader('templates'),
    FileSystemLoader('templates_admin'),
])

# Image upload configuration
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', 'dianne2005'),
        database=os.environ.get('DB_NAME', 'municipal_db')
    )

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_username' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

# Create necessary tables
def init_database():
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS images (
                id INT AUTO_INCREMENT PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                original_name VARCHAR(255),
                category VARCHAR(50) DEFAULT 'gallery',
                caption TEXT,
                file_size INT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contact_settings (
                id INT PRIMARY KEY DEFAULT 1,
                address VARCHAR(255),
                phone VARCHAR(50),
                email VARCHAR(100),
                facebook VARCHAR(255),
                twitter VARCHAR(255),
                hours VARCHAR(255),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("SELECT * FROM contact_settings WHERE id = 1")
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO contact_settings (id, address, phone, email, hours) VALUES (1, 
                    'Poblacion, Las Nieves, Agusan del Norte', 
                    '(088) 813-0110', 
                    'info@lasnieves.gov.ph',
                    'Monday - Friday, 8:00 AM - 5:00 PM'
                )
            """)
        
        db.commit()
        db.close()
    except Exception as e:
        print(f"Database init warning: {e}")

init_database()

# ════════════════════════════════════════════════════════════
#  PUBLIC ROUTES
# ════════════════════════════════════════════════════════════

@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM announcements ORDER BY date_posted DESC LIMIT 5")
    announcements = cursor.fetchall()
    
    # Get carousel images from database
    cursor.execute("SELECT filename, caption FROM images WHERE category = 'hero' ORDER BY uploaded_at DESC")
    carousel_images = cursor.fetchall()
    
    db.close()
    return render_template('index.html', announcements=announcements, carousel_images=carousel_images)

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/vision-mission')
def vision_mission():
    return render_template('vision_mission.html')

@app.route('/geography')
def geography():
    return render_template('geography.html')

@app.route('/population')
def population():
    return render_template('population.html')

@app.route('/officials')
def officials():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, full_name, position, office, email, rank_order, status FROM officials ORDER BY rank_order ASC, full_name ASC")
    officials = cursor.fetchall()
    db.close()
    return render_template('officials.html', officials=officials)

@app.route('/barangay-directory')
def barangay_directory():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM barangays ORDER BY name")
    barangays = cursor.fetchall()
    db.close()
    return render_template('barangay_directory.html', barangays=barangays)

@app.route('/announcements')
def announcements():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM announcements ORDER BY date_posted DESC")
    announcements = cursor.fetchall()
    db.close()
    return render_template('announcements.html', announcements=announcements)

@app.route('/projects')
def projects():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM projects ORDER BY id DESC")
    projects = cursor.fetchall()
    db.close()
    return render_template('projects.html', projects=projects)

@app.route('/emergency')
def emergency():
    return render_template('emergency.html')

@app.route('/gallery')
def gallery():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT filename, caption FROM images WHERE category = 'gallery' ORDER BY uploaded_at DESC")
    images = cursor.fetchall()
    db.close()
    return render_template('gallery.html', images=images)

@app.route('/calendar')
def calendar():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, title, event_date, location FROM events ORDER BY event_date ASC")
    events = cursor.fetchall()
    db.close()
    
    events_list = []
    for event in events:
        events_list.append({
            'id': event['id'],
            'title': event['title'],
            'event_date': event['event_date'].strftime('%Y-%m-%d'),
            'location': event['location'] if event['location'] else ''
        })
    
    from datetime import datetime
    current_date = datetime.now()
    
    return render_template('calendar.html', 
                         events_json=json.dumps(events_list),
                         current_month=current_date.strftime('%B'),
                         current_year=current_date.year)

@app.route('/emergency-services')
def emergency_services():
    return render_template('emergency_services.html')

@app.route('/events')
def events():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM events ORDER BY event_date ASC")
    events = cursor.fetchall()
    db.close()
    return render_template('events.html', events=events)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM contact_settings WHERE id = 1")
    contact_info = cursor.fetchone()
    db.close()
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        if name and message:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO inquiries (name, email, message) VALUES (%s, %s, %s)",
                (name, email, message)
            )
            db.commit()
            db.close()
            flash('Thank you! Your message has been sent.', 'success')
            return redirect(url_for('contact'))
        else:
            flash('Please fill in all required fields.', 'error')
    
    return render_template('contact.html', contact=contact_info)

@app.route('/municipal-seal')
def municipal_seal():
    return render_template('municipal_seal.html')

@app.route('/services')
def services():
    return render_template('services.html')

# ════════════════════════════════════════════════════════════
#  SEARCH API
# ════════════════════════════════════════════════════════════

@app.route('/api/search')
def search_api():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'announcements': [], 'officials': [], 'projects': [], 'events': []})
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT id, title, content, date_posted 
        FROM announcements 
        WHERE title LIKE %s OR content LIKE %s
        ORDER BY date_posted DESC
        LIMIT 5
    """, (f'%{query}%', f'%{query}%'))
    announcements = cursor.fetchall()
    for a in announcements:
        a['url'] = url_for('announcements')
        a['date_posted'] = a['date_posted'].strftime('%B %d, %Y') if a['date_posted'] else ''
    
    cursor.execute("""
        SELECT id, full_name, position, office 
        FROM officials 
        WHERE full_name LIKE %s OR position LIKE %s OR office LIKE %s
        LIMIT 5
    """, (f'%{query}%', f'%{query}%', f'%{query}%'))
    officials = cursor.fetchall()
    for o in officials:
        o['url'] = url_for('officials')
    
    cursor.execute("""
        SELECT id, title, description, status 
        FROM projects 
        WHERE title LIKE %s OR description LIKE %s
        LIMIT 5
    """, (f'%{query}%', f'%{query}%'))
    projects = cursor.fetchall()
    for p in projects:
        p['url'] = url_for('projects')
    
    cursor.execute("""
        SELECT id, title, event_date, location 
        FROM events 
        WHERE title LIKE %s OR location LIKE %s
        ORDER BY event_date ASC
        LIMIT 5
    """, (f'%{query}%', f'%{query}%'))
    events = cursor.fetchall()
    for e in events:
        e['url'] = url_for('events')
        e['event_date'] = e['event_date'].strftime('%B %d, %Y') if e['event_date'] else ''
    
    db.close()
    
    return jsonify({
        'announcements': announcements,
        'officials': officials,
        'projects': projects,
        'events': events
    })

@app.route('/api/events')
def api_events():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, title, event_date, location FROM events ORDER BY event_date ASC")
    events = cursor.fetchall()
    db.close()
    
    for event in events:
        event['event_date'] = event['event_date'].strftime('%Y-%m-%d')
    
    return jsonify(events)

# ════════════════════════════════════════════════════════════
#  ADMIN ROUTES
# ════════════════════════════════════════════════════════════

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            session['admin_username'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            error = 'Invalid username or password. Please try again.'
    return render_template('admin_login.html', error=error)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_username', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) AS cnt FROM announcements")
    announcements_count = cursor.fetchone()['cnt']
    cursor.execute("SELECT COUNT(*) AS cnt FROM officials")
    officials_count = cursor.fetchone()['cnt']
    cursor.execute("SELECT COUNT(*) AS cnt FROM projects")
    projects_count = cursor.fetchone()['cnt']
    cursor.execute("SELECT COUNT(*) AS cnt FROM inquiries WHERE status='pending' OR status IS NULL")
    inquiries_count = cursor.fetchone()['cnt']
    cursor.execute("SELECT COUNT(*) AS cnt FROM barangays")
    barangays_count = cursor.fetchone()['cnt']
    cursor.execute("SELECT COUNT(*) AS cnt FROM events")
    events_count = cursor.fetchone()['cnt']
    db.close()
    return render_template('admin_dashboard.html',
        announcements_count=announcements_count,
        officials_count=officials_count,
        projects_count=projects_count,
        inquiries_count=inquiries_count,
        barangays_count=barangays_count,
        events_count=events_count
    )

# ==================== BARANGAY MANAGEMENT ====================

@app.route('/admin/barangays')
@admin_required
def admin_barangays():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM barangays ORDER BY name")
    barangays = cursor.fetchall()
    db.close()
    return render_template('admin_barangays.html', barangays=barangays)

@app.route('/admin/barangays/new', methods=['GET', 'POST'])
@admin_required
def admin_barangay_new():
    if request.method == 'POST':
        name = request.form['name']
        captain = request.form.get('captain', '')
        contact_number = request.form.get('contact_number', '')
        population = request.form.get('population', 0)
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO barangays (name, captain, contact_number, population) 
            VALUES (%s, %s, %s, %s)
        """, (name, captain, contact_number, population))
        db.commit()
        db.close()
        return redirect(url_for('admin_barangays'))
    
    return render_template('admin_barangays_form.html', barangay=None)

@app.route('/admin/barangays/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_barangay_edit(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    if request.method == 'POST':
        name = request.form['name']
        captain = request.form.get('captain', '')
        contact_number = request.form.get('contact_number', '')
        population = request.form.get('population', 0)
        
        cursor.execute("""
            UPDATE barangays 
            SET name=%s, captain=%s, contact_number=%s, population=%s 
            WHERE id=%s
        """, (name, captain, contact_number, population, id))
        db.commit()
        db.close()
        return redirect(url_for('admin_barangays'))
    
    cursor.execute("SELECT * FROM barangays WHERE id=%s", (id,))
    barangay = cursor.fetchone()
    db.close()
    return render_template('admin_barangays_form.html', barangay=barangay)

@app.route('/admin/barangays/delete/<int:id>')
@admin_required
def admin_barangay_delete(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM barangays WHERE id=%s", (id,))
    db.commit()
    db.close()
    return redirect(url_for('admin_barangays'))

# ==================== CONTACT SETTINGS ====================

@app.route('/admin/contact-settings', methods=['GET', 'POST'])
@admin_required
def admin_contact_settings():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    if request.method == 'POST':
        cursor.execute("""
            UPDATE contact_settings 
            SET address=%s, phone=%s, email=%s, facebook=%s, twitter=%s, hours=%s
            WHERE id=1
        """, (
            request.form.get('address'),
            request.form.get('phone'),
            request.form.get('email'),
            request.form.get('facebook'),
            request.form.get('twitter'),
            request.form.get('hours')
        ))
        db.commit()
        db.close()
        flash('Contact information updated!', 'success')
        return redirect(url_for('admin_contact_settings'))
    
    cursor.execute("SELECT * FROM contact_settings WHERE id=1")
    settings = cursor.fetchone()
    db.close()
    
    if not settings:
        settings = {
            'address': 'Poblacion, Las Nieves, Agusan del Norte',
            'phone': '(088) 813-0110',
            'email': 'info@lasnieves.gov.ph',
            'facebook': '#',
            'twitter': '#',
            'hours': 'Monday - Friday, 8:00 AM - 5:00 PM'
        }
    
    return render_template('admin_contact.html', settings=settings)

# ==================== IMAGE MANAGEMENT ====================

@app.route('/admin/images')
@admin_required
def admin_images():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM images ORDER BY uploaded_at DESC")
    images = cursor.fetchall()
    db.close()
    
    image_list = []
    carousel_list = []
    logo_list = []
    
    for img in images:
        img['url'] = img['filename']  # filename now stores Cloudinary URL
        img['size'] = round(img['file_size'] / 1024, 1) if img['file_size'] else 0
        image_list.append(img)
        if img['category'] == 'hero':
            carousel_list.append(img)
        elif img['category'] == 'logo':
            logo_list.append(img)
    
    return render_template('admin_images.html', 
                         images=image_list, 
                         carousel_images=carousel_list,
                         logo_images=logo_list)

@app.route('/admin/upload-image', methods=['POST'])
@admin_required
def admin_upload_image():
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No file selected'})
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'File type not allowed'})
    
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        return jsonify({'success': False, 'error': 'File too large (max 5MB)'})
    
    category = request.form.get('category', 'gallery')
    caption = request.form.get('caption', '')
    original_filename = secure_filename(file.filename)

    try:
        import cloudinary
        import cloudinary.uploader
        cloudinary.config(
            cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME', 'dycblkudt'),
            api_key=os.environ.get('CLOUDINARY_API_KEY', '943494719821294'),
            api_secret=os.environ.get('CLOUDINARY_API_SECRET', '7FK57v3WJwLwrdLdF8iug99LMbE')
        )
        upload_result = cloudinary.uploader.upload(file, folder=f"municipal-site/{category}")
        image_url = upload_result['secure_url']
    except Exception as e:
        return jsonify({'success': False, 'error': f'Upload failed: {str(e)}'})
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO images (filename, original_name, category, caption, file_size)
        VALUES (%s, %s, %s, %s, %s)
    """, (image_url, original_filename, category, caption, file_size))
    db.commit()
    db.close()
    
    return jsonify({'success': True, 'filename': image_url, 'url': image_url})

@app.route('/admin/delete-image/<filename>', methods=['DELETE'])
@admin_required
def admin_delete_image(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM images WHERE filename = %s", (filename,))
    db.commit()
    db.close()
    
    return jsonify({'success': True})

# ==================== ANNOUNCEMENTS MANAGEMENT ====================

@app.route('/admin/announcements')
@admin_required
def admin_announcements():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM announcements ORDER BY date_posted DESC")
    announcements = cursor.fetchall()
    db.close()
    return render_template('admin_announcements.html', announcements=announcements)

@app.route('/admin/announcements/new', methods=['GET', 'POST'])
@admin_required
def admin_announcement_new():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO announcements (title, content, posted_by, date_posted) VALUES (%s, %s, %s, %s)",
            (title, content, session.get('admin_username', 'Admin'), datetime.now())
        )
        db.commit()
        db.close()
        flash('Announcement published!', 'success')
        return redirect(url_for('admin_announcements'))
    return render_template('admin_announcements_form.html', announcement=None)

@app.route('/admin/announcements/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_announcement_edit(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        cursor.execute("UPDATE announcements SET title=%s, content=%s WHERE id=%s", (title, content, id))
        db.commit()
        db.close()
        flash('Announcement updated!', 'success')
        return redirect(url_for('admin_announcements'))
    cursor.execute("SELECT * FROM announcements WHERE id=%s", (id,))
    announcement = cursor.fetchone()
    db.close()
    return render_template('admin_announcements_form.html', announcement=announcement)

@app.route('/admin/announcements/delete/<int:id>')
@admin_required
def admin_announcement_delete(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM announcements WHERE id=%s", (id,))
    db.commit()
    db.close()
    flash('Announcement deleted.', 'success')
    return redirect(url_for('admin_announcements'))

# ==================== OFFICIALS MANAGEMENT (UPDATED - NO CONTACT/PHOTO) ====================

@app.route('/admin/officials')
@admin_required
def admin_officials():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, full_name, position, office, email, order_num, status, rank_order FROM officials ORDER BY rank_order ASC, full_name ASC")
    officials = cursor.fetchall()
    db.close()
    return render_template('admin_officials.html', officials=officials)

@app.route('/admin/officials/new', methods=['GET', 'POST'])
@admin_required
def admin_official_new():
    if request.method == 'POST':
        full_name = request.form['full_name']
        position = request.form['position']
        office = request.form.get('office', '')
        email = request.form.get('email', '')
        order_num = request.form.get('order_num', 0)
        status = request.form.get('status', 'active')
        rank_order = request.form.get('rank_order', 0)
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO officials (full_name, position, office, email, order_num, status, rank_order) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (full_name, position, office, email, order_num, status, rank_order))
        db.commit()
        db.close()
        flash('Official added!', 'success')
        return redirect(url_for('admin_officials'))
    return render_template('admin_officials_form.html', official=None)

@app.route('/admin/officials/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_official_edit(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        full_name = request.form['full_name']
        position = request.form['position']
        office = request.form.get('office', '')
        email = request.form.get('email', '')
        order_num = request.form.get('order_num', 0)
        status = request.form.get('status', 'active')
        rank_order = request.form.get('rank_order', 0)
        
        cursor.execute("""
            UPDATE officials 
            SET full_name=%s, position=%s, office=%s, email=%s, order_num=%s, status=%s, rank_order=%s 
            WHERE id=%s
        """, (full_name, position, office, email, order_num, status, rank_order, id))
        db.commit()
        db.close()
        flash('Official updated!', 'success')
        return redirect(url_for('admin_officials'))
    
    cursor.execute("SELECT * FROM officials WHERE id=%s", (id,))
    official = cursor.fetchone()
    db.close()
    return render_template('admin_officials_form.html', official=official)

@app.route('/admin/officials/delete/<int:id>')
@admin_required
def admin_official_delete(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM officials WHERE id=%s", (id,))
    db.commit()
    db.close()
    flash('Official removed.', 'success')
    return redirect(url_for('admin_officials'))

# ==================== PROJECTS MANAGEMENT ====================

@app.route('/admin/projects')
@admin_required
def admin_projects():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM projects ORDER BY id DESC")
    projects = cursor.fetchall()
    db.close()
    return render_template('admin_projects.html', projects=projects)

@app.route('/admin/projects/new', methods=['GET', 'POST'])
@admin_required
def admin_project_new():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        status = request.form.get('status', 'Ongoing')
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO projects (title, description, status) VALUES (%s, %s, %s)",
            (title, description, status)
        )
        db.commit()
        db.close()
        flash('Project added!', 'success')
        return redirect(url_for('admin_projects'))
    return render_template('admin_projects_form.html', project=None)

@app.route('/admin/projects/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_project_edit(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        status = request.form.get('status', 'Ongoing')
        cursor.execute(
            "UPDATE projects SET title=%s, description=%s, status=%s WHERE id=%s",
            (title, description, status, id)
        )
        db.commit()
        db.close()
        flash('Project updated!', 'success')
        return redirect(url_for('admin_projects'))
    cursor.execute("SELECT * FROM projects WHERE id=%s", (id,))
    project = cursor.fetchone()
    db.close()
    return render_template('admin_projects_form.html', project=project)

@app.route('/admin/projects/delete/<int:id>')
@admin_required
def admin_project_delete(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM projects WHERE id=%s", (id,))
    db.commit()
    db.close()
    flash('Project deleted.', 'success')
    return redirect(url_for('admin_projects'))

# ==================== EVENTS MANAGEMENT ====================

@app.route('/admin/events')
@admin_required
def admin_events():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM events ORDER BY event_date ASC")
    events = cursor.fetchall()
    db.close()
    return render_template('admin_events.html', events=events)

@app.route('/admin/events/new', methods=['GET', 'POST'])
@admin_required
def admin_event_new():
    if request.method == 'POST':
        title = request.form['title']
        event_date = request.form['event_date']
        location = request.form.get('location', '')
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO events (title, event_date, location) VALUES (%s, %s, %s)",
            (title, event_date, location)
        )
        db.commit()
        db.close()
        flash('Event added!', 'success')
        return redirect(url_for('admin_events'))
    return render_template('admin_events_form.html', event=None)

@app.route('/admin/events/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_event_edit(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        title = request.form['title']
        event_date = request.form['event_date']
        location = request.form.get('location', '')
        cursor.execute(
            "UPDATE events SET title=%s, event_date=%s, location=%s WHERE id=%s",
            (title, event_date, location, id)
        )
        db.commit()
        db.close()
        flash('Event updated!', 'success')
        return redirect(url_for('admin_events'))
    cursor.execute("SELECT * FROM events WHERE id=%s", (id,))
    event = cursor.fetchone()
    db.close()
    return render_template('admin_events_form.html', event=event)

@app.route('/admin/events/delete/<int:id>')
@admin_required
def admin_event_delete(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM events WHERE id=%s", (id,))
    db.commit()
    db.close()
    flash('Event deleted.', 'success')
    return redirect(url_for('admin_events'))

# ==================== INQUIRIES MANAGEMENT ====================

@app.route('/admin/inquiries')
@admin_required
def admin_inquiries():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inquiries ORDER BY id DESC")
    inquiries = cursor.fetchall()
    db.close()
    return render_template('admin_inquiries.html', inquiries=inquiries)

@app.route('/admin/inquiries/mark-read/<int:id>', methods=['POST'])
@admin_required
def admin_inquiry_mark_read(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE inquiries SET status = 'read' WHERE id = %s", (id,))
    db.commit()
    db.close()
    flash('Inquiry marked as read.', 'success')
    return redirect(url_for('admin_inquiries'))

# ==================== EMERGENCY SETTINGS ====================

@app.route('/admin/emergency')
@admin_required
def admin_emergency():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM emergency_settings WHERE id = 1")
    settings = cursor.fetchone()
    db.close()
    return render_template('admin_emergency.html', settings=settings)

@app.route('/admin/emergency/edit', methods=['GET', 'POST'])
@admin_required
def admin_emergency_edit():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    if request.method == 'POST':
        cursor.execute("""
            UPDATE emergency_settings SET
                police_hotline = %s,
                police_mobile = %s,
                police_address = %s,
                ems_hotline = %s,
                ems_mobile = %s,
                rhu_contact = %s,
                fire_hotline = %s,
                fire_mobile = %s,
                mdrmo_hotline = %s,
                mdrmo_mobile = %s,
                mdrmo_email = %s,
                flood_tips = %s,
                fire_tips = %s,
                earthquake_tips = %s,
                health_tips = %s,
                updated_at = NOW()
            WHERE id = 1
        """, (
            request.form.get('police_hotline'),
            request.form.get('police_mobile'),
            request.form.get('police_address'),
            request.form.get('ems_hotline'),
            request.form.get('ems_mobile'),
            request.form.get('rhu_contact'),
            request.form.get('fire_hotline'),
            request.form.get('fire_mobile'),
            request.form.get('mdrmo_hotline'),
            request.form.get('mdrmo_mobile'),
            request.form.get('mdrmo_email'),
            request.form.get('flood_tips'),
            request.form.get('fire_tips'),
            request.form.get('earthquake_tips'),
            request.form.get('health_tips')
        ))
        db.commit()
        db.close()
        flash('Emergency settings updated!', 'success')
        return redirect(url_for('admin_emergency'))
    
    cursor.execute("SELECT * FROM emergency_settings WHERE id = 1")
    settings = cursor.fetchone()
    db.close()
    return render_template('admin_emergency_form.html', settings=settings)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("✅ LAS NIEVES WEBSITE IS RUNNING!")
    print("="*50)
    print("📍 PUBLIC URL:  http://127.0.0.1:5000/")
    print("📍 ADMIN URL:   http://127.0.0.1:5000/admin/login")
    print("👤 Username:    admin")
    print("🔑 Password:    admin123")
    print("="*50 + "\n")
    app.run(debug=True, host='127.0.0.1', port=5000)
