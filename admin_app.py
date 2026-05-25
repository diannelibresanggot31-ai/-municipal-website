from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import mysql.connector
from datetime import datetime, date
from functools import wraps
import os
import json
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader

app = Flask(__name__, template_folder='templates_admin')
app.secret_key = os.environ.get('SECRET_KEY', 'admin_secret_key_2026')

# Cloudinary configuration - reads from environment variables
cloudinary.config(
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME', 'dycblkudt'),
    api_key = os.environ.get('CLOUDINARY_API_KEY', '943494719821294'),
    api_secret = os.environ.get('CLOUDINARY_API_SECRET', '7FK57v3WJwLwrdLdF8iug99LMbE')
)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', 'dianne2005'),
        database=os.environ.get('DB_NAME', 'municipal_db')
    )

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.context_processor
def inject_globals():
    return dict(session=session, datetime=datetime, today=date.today())

# ==================== LOGIN/LOGOUT ====================
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            session['admin_username'] = username
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid username or password.'
    return render_template('admin_login.html', error=error)

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('login'))

# ==================== DASHBOARD ====================
@app.route('/dashboard')
@app.route('/admin/dashboard')
@login_required
def dashboard():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT COUNT(*) AS cnt FROM announcements")
    announcements_count = cursor.fetchone()['cnt']
    
    cursor.execute("SELECT COUNT(*) AS cnt FROM officials")
    officials_count = cursor.fetchone()['cnt']
    
    cursor.execute("SELECT COUNT(*) AS cnt FROM projects")
    projects_count = cursor.fetchone()['cnt']
    
    cursor.execute("SELECT COUNT(*) AS cnt FROM events")
    events_count = cursor.fetchone()['cnt']
    
    cursor.execute("SELECT COUNT(*) AS cnt FROM barangays")
    barangays_count = cursor.fetchone()['cnt']
    
    cursor.execute("SELECT COUNT(*) AS cnt FROM images")
    images_count = cursor.fetchone()['cnt']
    
    # Fetch recent items
    cursor.execute("SELECT id, title, date_posted FROM announcements ORDER BY date_posted DESC LIMIT 5")
    recent_announcements = cursor.fetchall()
    
    cursor.execute("SELECT id, title FROM projects ORDER BY id DESC LIMIT 5")
    recent_projects = cursor.fetchall()
    
    db.close()
    return render_template('admin_dashboard.html',
        announcements_count=announcements_count,
        officials_count=officials_count,
        projects_count=projects_count,
        events_count=events_count,
        barangays_count=barangays_count,
        images_count=images_count,
        recent_announcements=recent_announcements,
        recent_projects=recent_projects,
        current_user=session.get('admin_username', 'Admin'),
        current_date=date.today()
    )

# ==================== ANNOUNCEMENTS ====================
@app.route('/admin/announcements')
@login_required
def announcements():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM announcements ORDER BY date_posted DESC")
    announcements = cursor.fetchall()
    db.close()
    return render_template('admin_announcements.html', announcements=announcements)

@app.route('/admin/announcements/new', methods=['GET', 'POST'])
@login_required
def add_announcement():
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
        flash('Announcement published successfully!', 'success')
        return redirect(url_for('announcements'))
    return render_template('admin_announcements_form.html', announcement=None)

@app.route('/admin/announcements/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_announcement(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        cursor.execute("UPDATE announcements SET title=%s, content=%s WHERE id=%s", (title, content, id))
        db.commit()
        db.close()
        flash('Announcement updated successfully!', 'success')
        return redirect(url_for('announcements'))
    cursor.execute("SELECT * FROM announcements WHERE id=%s", (id,))
    announcement = cursor.fetchone()
    db.close()
    return render_template('admin_announcements_form.html', announcement=announcement)

@app.route('/admin/announcements/delete/<int:id>')
@login_required
def delete_announcement(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM announcements WHERE id=%s", (id,))
    db.commit()
    db.close()
    flash('Announcement deleted successfully!', 'success')
    return redirect(url_for('announcements'))

# ==================== OFFICIALS (UPDATED - NO CONTACT/PHOTO) ====================
@app.route('/admin/officials')
@login_required
def officials():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, full_name, position, office, email, order_num, rank_order, status FROM officials ORDER BY rank_order ASC, full_name ASC")
    officials = cursor.fetchall()
    db.close()
    return render_template('admin_officials.html', officials=officials)

@app.route('/admin/officials/new', methods=['GET', 'POST'])
@login_required
def add_official():
    if request.method == 'POST':
        full_name = request.form['full_name']
        position = request.form['position']
        office = request.form.get('office', '')
        email = request.form.get('email', '')
        order_num = request.form.get('order_num', 0)
        rank_order = request.form.get('rank_order', 0)
        status = request.form.get('status', 'active')
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO officials (full_name, position, office, email, order_num, rank_order, status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (full_name, position, office, email, order_num, rank_order, status))
        db.commit()
        db.close()
        flash('Official added successfully!', 'success')
        return redirect(url_for('officials'))
    return render_template('admin_officials_form.html', official=None)

@app.route('/admin/officials/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_official(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        full_name = request.form['full_name']
        position = request.form['position']
        office = request.form.get('office', '')
        email = request.form.get('email', '')
        order_num = request.form.get('order_num', 0)
        rank_order = request.form.get('rank_order', 0)
        status = request.form.get('status', 'active')
        
        cursor.execute("""
            UPDATE officials 
            SET full_name=%s, position=%s, office=%s, email=%s, order_num=%s, rank_order=%s, status=%s 
            WHERE id=%s
        """, (full_name, position, office, email, order_num, rank_order, status, id))
        db.commit()
        db.close()
        flash('Official updated successfully!', 'success')
        return redirect(url_for('officials'))
    
    cursor.execute("SELECT * FROM officials WHERE id=%s", (id,))
    official = cursor.fetchone()
    db.close()
    return render_template('admin_officials_form.html', official=official)

@app.route('/admin/officials/delete/<int:id>')
@login_required
def delete_official(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM officials WHERE id=%s", (id,))
    db.commit()
    db.close()
    flash('Official deleted successfully!', 'success')
    return redirect(url_for('officials'))

# ==================== PROJECTS ====================
@app.route('/admin/projects')
@login_required
def projects():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM projects ORDER BY id DESC")
    projects = cursor.fetchall()
    db.close()
    return render_template('admin_projects.html', projects=projects)

@app.route('/admin/projects/new', methods=['GET', 'POST'])
@login_required
def add_project():
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
        flash('Project added successfully!', 'success')
        return redirect(url_for('projects'))
    return render_template('admin_projects_form.html', project=None)

@app.route('/admin/projects/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_project(id):
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
        flash('Project updated successfully!', 'success')
        return redirect(url_for('projects'))
    cursor.execute("SELECT * FROM projects WHERE id=%s", (id,))
    project = cursor.fetchone()
    db.close()
    return render_template('admin_projects_form.html', project=project)

@app.route('/admin/projects/delete/<int:id>')
@login_required
def delete_project(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM projects WHERE id=%s", (id,))
    db.commit()
    db.close()
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('projects'))

# ==================== EVENTS ====================
@app.route('/admin/events')
@login_required
def events():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM events ORDER BY event_date ASC")
    events = cursor.fetchall()
    db.close()
    return render_template('admin_events.html', events=events)

@app.route('/admin/events/new', methods=['GET', 'POST'])
@login_required
def add_event():
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
        flash('Event added successfully!', 'success')
        return redirect(url_for('events'))
    return render_template('admin_events_form.html', event=None)

@app.route('/admin/events/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_event(id):
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
        flash('Event updated successfully!', 'success')
        return redirect(url_for('events'))
    cursor.execute("SELECT * FROM events WHERE id=%s", (id,))
    event = cursor.fetchone()
    db.close()
    return render_template('admin_events_form.html', event=event)

@app.route('/admin/events/delete/<int:id>')
@login_required
def delete_event(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM events WHERE id=%s", (id,))
    db.commit()
    db.close()
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('events'))

# ==================== BARANGAYS ====================
@app.route('/admin/barangays')
@login_required
def admin_barangays():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM barangays ORDER BY name")
    barangays = cursor.fetchall()
    db.close()
    return render_template('admin_barangays.html', barangays=barangays)

@app.route('/admin/barangays/new', methods=['GET', 'POST'])
@login_required
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
        flash('Barangay added successfully!', 'success')
        return redirect(url_for('admin_barangays'))
    return render_template('admin_barangays_form.html', barangay=None)

@app.route('/admin/barangays/edit/<int:id>', methods=['GET', 'POST'])
@login_required
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
        flash('Barangay updated successfully!', 'success')
        return redirect(url_for('admin_barangays'))
    
    cursor.execute("SELECT * FROM barangays WHERE id=%s", (id,))
    barangay = cursor.fetchone()
    db.close()
    return render_template('admin_barangays_form.html', barangay=barangay)

@app.route('/admin/barangays/delete/<int:id>')
@login_required
def admin_barangay_delete(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM barangays WHERE id=%s", (id,))
    db.commit()
    db.close()
    flash('Barangay deleted successfully!', 'success')
    return redirect(url_for('admin_barangays'))

# ==================== IMAGE MANAGEMENT ====================
@app.route('/admin/images')
@login_required
def admin_images():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM images ORDER BY uploaded_at DESC")
    images = cursor.fetchall()
    db.close()
    
    carousel_images = []
    logo_images = []
    for img in images:
        img['url'] = img['filename']
        img['size'] = round(img['file_size'] / 1024, 1) if img['file_size'] else 0
        if img['category'] == 'hero':
            carousel_images.append(img)
        elif img['category'] == 'logo':
            logo_images.append(img)
    
    return render_template('admin_images.html', 
                         images=images, 
                         carousel_images=carousel_images,
                         logo_images=logo_images)

@app.route('/admin/upload-image', methods=['POST'])
@login_required
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
        upload_preset = os.environ.get('CLOUDINARY_UPLOAD_PRESET', '')
        if not upload_preset:
            return jsonify({
                'success': False, 
                'error': 'Upload preset not configured. Set CLOUDINARY_UPLOAD_PRESET environment variable.'
            })
        
        upload_result = cloudinary.uploader.upload(
            file,
            folder=f"municipal-site/{category}",
            resource_type="image",
            upload_preset=upload_preset
        )
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

@app.route('/admin/delete-image/<path:filename>', methods=['DELETE'])
@login_required
def admin_delete_image(filename):
    try:
        if 'cloudinary.com' in filename:
            parts = filename.split('/')
            upload_idx = parts.index('upload') if 'upload' in parts else -1
            if upload_idx != -1:
                public_id_parts = parts[upload_idx+2:]
                public_id = '/'.join(public_id_parts)
                public_id = public_id.rsplit('.', 1)[0]
                cloudinary.uploader.destroy(public_id)
    except Exception:
        pass

    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM images WHERE filename = %s", (filename,))
    db.commit()
    db.close()
    
    return jsonify({'success': True})

# ==================== CONTACT SETTINGS ====================
@app.route('/admin/contact-settings', methods=['GET', 'POST'])
@login_required
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
        flash('Contact settings updated successfully!', 'success')
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

# ==================== EMERGENCY ====================
@app.route('/admin/emergency')
@login_required
def emergency():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM emergency_settings WHERE id = 1")
    settings = cursor.fetchone()
    db.close()
    
    if not settings:
        settings = {
            'police_hotline': '117',
            'police_mobile': '0917-123-4567',
            'police_address': 'Poblacion, Las Nieves',
            'ems_hotline': '911',
            'ems_mobile': '0920-888-9999',
            'rhu_contact': '(085) 123-4567',
            'fire_hotline': '160',
            'fire_mobile': '0918-555-7777',
            'mdrmo_hotline': '(085) 342-5678',
            'mdrmo_mobile': '0919-777-8888',
            'mdrmo_email': 'drrmo@lasnieves.gov.ph',
            'flood_tips': 'Stay informed, evacuate when advised, avoid flood waters, keep emergency kit ready.',
            'fire_tips': 'Check electrical connections, don\'t leave cooking unattended, know fire exits.',
            'earthquake_tips': 'Drop, Cover, and Hold On. Stay away from windows and heavy objects.',
            'health_tips': 'Call 911 immediately, provide first aid if trained, stay calm.'
        }
    
    return render_template('admin_emergency.html', settings=settings)

@app.route('/admin/emergency/edit', methods=['GET', 'POST'])
@login_required
def emergency_edit():
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
        flash('Emergency settings updated successfully!', 'success')
        return redirect(url_for('emergency'))
    
    cursor.execute("SELECT * FROM emergency_settings WHERE id = 1")
    settings = cursor.fetchone()
    db.close()
    
    if not settings:
        settings = {
            'police_hotline': '117',
            'police_mobile': '0917-123-4567',
            'police_address': 'Poblacion, Las Nieves',
            'ems_hotline': '911',
            'ems_mobile': '0920-888-9999',
            'rhu_contact': '(085) 123-4567',
            'fire_hotline': '160',
            'fire_mobile': '0918-555-7777',
            'mdrmo_hotline': '(085) 342-5678',
            'mdrmo_mobile': '0919-777-8888',
            'mdrmo_email': 'drrmo@lasnieves.gov.ph',
            'flood_tips': 'Stay informed, evacuate when advised, avoid flood waters, keep emergency kit ready.',
            'fire_tips': 'Check electrical connections, don\'t leave cooking unattended, know fire exits.',
            'earthquake_tips': 'Drop, Cover, and Hold On. Stay away from windows and heavy objects.',
            'health_tips': 'Call 911 immediately, provide first aid if trained, stay calm.'
        }
    
    return render_template('admin_emergency_form.html', settings=settings)

# ==================== PAGE CONTENT ====================
@app.route('/admin/page-content')
@login_required
def page_content():
    # Page Content feature removed — redirect to dashboard
    flash('Page Content feature has been removed.', 'info')
    return redirect(url_for('dashboard'))

@app.route('/admin/page-content/edit/<page_name>', methods=['GET', 'POST'])
@login_required
def edit_page_content(page_name):
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("SELECT * FROM page_content WHERE page_name = %s", (page_name,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE page_content 
                SET page_title=%s, meta_description=%s, hero_title=%s, hero_subtitle=%s, 
                    hero_image=%s, content_body=%s, sidebar_title=%s, sidebar_content=%s,
                    cta_text=%s, cta_link=%s, status=%s, show_in_nav=%s, updated_at=%s
                WHERE page_name=%s
            """, (
                request.form.get('page_title', ''),
                request.form.get('meta_description', ''),
                request.form.get('hero_title', ''),
                request.form.get('hero_subtitle', ''),
                request.form.get('hero_image', ''),
                request.form.get('content_body', ''),
                request.form.get('sidebar_title', ''),
                request.form.get('sidebar_content', ''),
                request.form.get('cta_text', ''),
                request.form.get('cta_link', ''),
                request.form.get('status', 'draft'),
                request.form.get('show_in_nav', 'no'),
                datetime.now(),
                page_name
            ))
        else:
            cursor.execute("""
                INSERT INTO page_content (page_name, page_title, meta_description, hero_title, 
                    hero_subtitle, hero_image, content_body, sidebar_title, sidebar_content,
                    cta_text, cta_link, status, show_in_nav, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                page_name,
                request.form.get('page_title', ''),
                request.form.get('meta_description', ''),
                request.form.get('hero_title', ''),
                request.form.get('hero_subtitle', ''),
                request.form.get('hero_image', ''),
                request.form.get('content_body', ''),
                request.form.get('sidebar_title', ''),
                request.form.get('sidebar_content', ''),
                request.form.get('cta_text', ''),
                request.form.get('cta_link', ''),
                request.form.get('status', 'draft'),
                request.form.get('show_in_nav', 'no'),
                datetime.now(),
                datetime.now()
            ))
        
        db.commit()
        db.close()
        
        return redirect(url_for('page_content'))
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM page_content WHERE page_name = %s", (page_name,))
    page = cursor.fetchone()
    db.close()
    
    if not page:
        page = {
            'page_title': f'{page_name.capitalize()} - Las Nieves',
            'meta_description': f'Welcome to the {page_name} page of Las Nieves municipality',
            'hero_title': f'Welcome to {page_name.capitalize()}',
            'hero_subtitle': 'Your gateway to Las Nieves',
            'hero_image': '',
            'content_body': f'<h1>{page_name.capitalize()}</h1><p>Content for the {page_name} page goes here.</p>',
            'sidebar_title': 'Quick Links',
            'sidebar_content': '<ul><li>About Us</li><li>Services</li><li>Contact</li></ul>',
            'cta_text': 'Learn More',
            'cta_link': '/contact',
            'status': 'draft',
            'show_in_nav': 'no'
        }
    
    return render_template('admin_page_content_edit.html', 
                         page_name=page_name,
                         page_title=page.get('page_title', ''),
                         meta_description=page.get('meta_description', ''),
                         hero_title=page.get('hero_title', ''),
                         hero_subtitle=page.get('hero_subtitle', ''),
                         hero_image=page.get('hero_image', ''),
                         content_body=page.get('content_body', ''),
                         sidebar_title=page.get('sidebar_title', ''),
                         sidebar_content=page.get('sidebar_content', ''),
                         cta_text=page.get('cta_text', ''),
                         cta_link=page.get('cta_link', ''),
                         status=page.get('status', 'draft'),
                         show_in_nav=page.get('show_in_nav', 'no'))

if __name__ == '__main__':
    print("\n" + "="*50)
    print("✅ ADMIN PANEL IS RUNNING!")
    print("="*50)
    print("📍 URL:      http://127.0.0.1:5001/")
    print("👤 Username: admin")
    print("🔑 Password: admin123")
    print("="*50 + "\n")
    print("ADMIN MENU:")
    print("  - Dashboard")
    print("  - Announcements")
    print("  - Projects")
    print("  - Officials")
    print("  - Events")
    print("  - Barangays")
    print("  - Image Manager")
    print("  - Emergency Info")
    print("  - Contact Settings")
    print("  - Page Content")
    print("="*50 + "\n")
    app.run(debug=True, host='127.0.0.1', port=5001)