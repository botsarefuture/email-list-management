from flask import Blueprint, request, render_template, redirect, url_for, current_app, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_pymongo import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from DatabaseManager import DatabaseManager
from usermodel import User

# Initialize Blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Initialize Flask-Login
login_manager = LoginManager()
#login_manager.init_app(current_app)

users_collection = "service_users"

# Access Flask app context for extensions
def get_mongo():
    db_man = DatabaseManager().get_instance()
    db = db_man.get_db()
    return db

def get_email_service():
    return current_app.email_service

# Load user callback
@login_manager.user_loader
def load_user(user_id):
    db = get_mongo()
    user_data = db[users_collection].find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(_id=user_data["_id"], username=user_data["username"], password=user_data["password"], hashed=True)
    return None

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login route for admin."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        db = get_mongo()
        user_data = db[users_collection].find_one({"username": username})
        
        if user_data and User(_id=user_data["_id"], username=user_data["username"], password=user_data["password"], hashed=True).verify_password(password):
            user = User(_id=user_data["_id"], username=user_data["username"], password=user_data["password"], hashed=True)
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('admin.manage_lists'))

        flash('Invalid username or password', 'error')

    return render_template('admin/login.html')

@admin_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    db = get_mongo()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        domain = request.form.get("domain")  # Get the domain from the form
        
        # Check if username or email already exists
        if db[users_collection].find_one({"username": username}):
            flash('Käyttäjänimi on jo käytössä. Valitse toinen.', 'danger')
            return redirect(url_for('admin.register'))
        
        if db[users_collection].find_one({"email": email}):
            flash('Sähköposti on jo käytössä. Valitse toinen.', 'danger')
            return redirect(url_for('admin.reregistergister'))
        
        # Create a new user document
        new_user = {
            "username": username,
            "email": email,
            "domain": domain,
            "password": hash_password(password)  # Hash the password
        }
        
        # Insert the new user document into the collection
        db[users_collection].insert_one(new_user)
        
        flash('Käyttäjä rekisteröity onnistuneesti!', 'success')
        return redirect(url_for('admin.login'))  # Redirect to the registration page or another page
    
    return render_template('admin/register.html')  # Render the registration template

def hash_password(password):
    """Hash the password"""
    return generate_password_hash(password)

@admin_bp.route('/logout')
@login_required
def logout():
    """Logout route for admin."""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('admin.login'))

@admin_bp.route("/lists", methods=["GET"])
@login_required
def manage_lists():
    """View to manage email lists."""
    mongo = get_mongo()
    lists = list(mongo.db.lists.find())
    return render_template('admin/manage_lists.html', lists=lists)

@admin_bp.route("/lists/create", methods=["GET", "POST"])
@login_required
def create_list():
    """Create a new email list."""
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description", "")
        sender_email = request.form.get("sender_email")

        if not name:
            flash('Missing list name', 'error')
            return redirect(url_for('admin.create_list'))

        mongo = get_mongo()
        if mongo.db.lists.find_one({"name": name}):
            flash('List with that name already exists', 'error')
            return redirect(url_for('admin.create_list'))

        new_list = {
            "name": name,
            "description": description,
            "sender_email": sender_email
        }
        mongo.db.lists.insert_one(new_list)
        flash('New list created successfully!', 'success')
        return redirect(url_for('admin.manage_lists'))

    return render_template('admin/edit_list.html', title='Create New List')

@admin_bp.route("/lists/<list_id>/edit", methods=["GET", "POST"])
@login_required
def edit_list(list_id):
    """Edit an existing email list."""
    mongo = get_mongo()
    list_data = mongo.db.lists.find_one({"_id": ObjectId(list_id)})

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        sender_email = request.form.get("sender_email")

        if not name:
            flash('List name is required', 'error')
            return redirect(url_for('admin.edit_list', list_id=list_id))

        update_data = {
            "name": name,
            "description": description,
            "sender_email": sender_email
        }
        mongo.db.lists.update_one({"_id": ObjectId(list_id)}, {"$set": update_data})
        flash('List updated successfully!', 'success')
        return redirect(url_for('admin.manage_lists'))

    return render_template('admin/edit_list.html', title='Edit List', list=list_data)

@admin_bp.route("/lists/<list_id>/delete", methods=["POST"])
@login_required
def delete_list(list_id):
    """Delete an email list."""
    mongo = get_mongo()
    result = mongo.db.lists.find_one_and_delete({"_id": ObjectId(list_id)})
    
    if result:
        flash('List deleted successfully!', 'success')
    else:
        flash('List not found', 'error')
    
    return redirect(url_for('admin.manage_lists'))

@admin_bp.route('/send-email', methods=['GET', 'POST'])
@login_required
def send_email():
    """Send email to subscribers of a specified list."""
    if request.method == 'POST':
        list_id = request.form.get('list_id')
        subject = request.form.get('subject')
        body = request.form.get('email_body')
        
        if not list_id or not subject or not body:
            flash('All fields are required', 'error')
            return redirect(url_for('admin.send_email'))
        
        mongo = get_mongo()
        list_data = mongo.db.lists.find_one({"_id": ObjectId(list_id)})
        
        if not list_data:
            flash('List not found', 'error')
            return redirect(url_for('admin.send_email'))
        
        subscribers = mongo.db.users.find({"list_id": list_id, "confirmed": True})
        recipient_emails = [user['email'] for user in subscribers]

        email_service = get_email_service()
        errors = []

        for email in recipient_emails:
            try:
                email_service.send_custom_email(email, subject, body)
            except Exception as e:
                current_app.logger.error(f"Error sending email to {email}: {e}")
                errors.append(email)

        if errors:
            flash(f'Errors occurred while sending emails to: {", ".join(errors)}', 'error')
        else:
            flash('Emails sent successfully!', 'success')
        return redirect(url_for('admin.send_email'))

    mongo = get_mongo()
    lists = list(mongo.db.lists.find())
    return render_template('admin/send_email.html', lists=lists)

# Domain management routes
@admin_bp.route("/domains", methods=["GET"])
@login_required
def manage_domains():
    """View to manage email sending domains."""
    mongo = get_mongo()
    domains = list(mongo.db.domains.find({"user": ObjectId(current_user._id)}))
    txt_record = current_user.txt_record
    return render_template('admin/manage_domains.html', domains=domains, txt_record=txt_record)

@admin_bp.route("/domains/create", methods=["GET", "POST"])
@login_required
def create_domain():
    """Add a new domain for sending emails."""
    if request.method == "POST":
        domain = request.form.get("domain")

        if not domain:
            flash('Missing domain name', 'error')
            return redirect(url_for('admin.create_domain'))

        mongo = get_mongo()
        if mongo.db.domains.find_one({"domain": domain}):
            flash('Domain already exists', 'error')
            return redirect(url_for('admin.create_domain'))

        new_domain = {
            "domain": domain,
            "dns_records": {
                "SPF": f"v=spf1 include:{domain} ~all",
                "DKIM": f"Add DKIM record for {domain}",
                "DMARC": f"Add DMARC record for {domain}"
            },
            "user": ObjectId(current_user._id)
        }
        mongo.db.domains.insert_one(new_domain)
        flash('Domain added successfully! Please set up the required DNS records.', 'success')
        return redirect(url_for('admin.manage_domains'))

    return render_template('admin/edit_domain.html', title='Add New Domain')

@admin_bp.route("/domains/<domain_id>/edit", methods=["GET", "POST"])
@login_required
def edit_domain(domain_id):
    """Edit an existing email sending domain."""
    mongo = get_mongo()
    domain_data = mongo.db.domains.find_one({"_id": ObjectId(domain_id)})

    if request.method == "POST":
        domain = request.form.get("domain")

        if not domain:
            flash('Domain name is required', 'error')
            return redirect(url_for('admin.edit_domain', domain_id=domain_id))

        update_data = {
            "domain": domain,
            "dns_records": {
                "SPF": f"v=spf1 include:{domain} ~all",
                "DKIM": f"Add DKIM record for {domain}",
                "DMARC": f"Add DMARC record for {domain}"
            }
        }
        mongo.db.domains.update_one({"_id": ObjectId(domain_id)}, {"$set": update_data})
        flash('Domain updated successfully!', 'success')
        return redirect(url_for('admin.manage_domains'))

    return render_template('admin/edit_domain.html', title='Edit Domain', domain=domain_data)

@admin_bp.route("/domains/<domain_id>/delete", methods=["POST"])
@login_required
def delete_domain(domain_id):
    """Delete an email sending domain."""
    mongo = get_mongo()
    result = mongo.db.domains.find_one_and_delete({"_id": ObjectId(domain_id)})
    
    if result:
        flash('Domain deleted successfully!', 'success')
    else:
        flash('Domain not found', 'error')
    
    return redirect(url_for('admin.manage_domains'))

# This file should be imported and registered in your main app
