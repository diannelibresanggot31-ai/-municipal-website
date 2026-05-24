import os

templates = {
    'admin_projects.html': '''
{% extends "admin_dashboard.html" %}
{% block content %}
<h2>Manage Projects</h2>
<a href="/admin/projects/add">Add Project</a>
{% endblock %}
''',
    'admin_projects_form.html': '<h2>Project Form</h2><form method="POST"><input name="title"><textarea name="description"></textarea><button type="submit">Save</button></form>',
    'admin_officials.html': '<h2>Officials</h2><a href="/admin/officials/add">Add Official</a>',
    'admin_officials_form.html': '<h2>Official Form</h2><form method="POST"><input name="full_name"><input name="position"><button type="submit">Save</button></form>',
    'admin_emergency.html': '<h2>Emergency Contacts</h2><a href="/admin/emergency/add">Add Contact</a>',
    'admin_emergency_form.html': '<h2>Emergency Form</h2><form method="POST"><input name="service_name"><input name="contact_number"><button type="submit">Save</button></form>',
    'admin_inquiries.html': '<h2>Inquiries</h2>',
    'admin_events.html': '<h2>Events</h2><a href="/admin/events/add">Add Event</a>',
    'admin_events_form.html': '<h2>Event Form</h2><form method="POST"><input name="title"><input type="date" name="event_date"><button type="submit">Save</button></form>',
}

for filename, content in templates.items():
    path = f"templates_admin/{filename}"
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created: {filename}")

print("All templates created!")