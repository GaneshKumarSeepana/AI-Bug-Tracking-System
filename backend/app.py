from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
import flask
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from config import Config
import os, sys
from functools import wraps
from bson.objectid import ObjectId
import datetime

# Add m1 directory to path for AI models
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Try importing prediction model, handle if not ready
try:
    from m1.predict import predict_priority_and_type
except ImportError:
    predict_priority_and_type = None

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

app.config.from_object(Config)
# from mongita import MongitaClientDisk

# # NETWORK FIX: Use local embedded database to bypass SSL/Firewall issues
# print("⚠️ USING LOCAL DATABASE (Mongita) due to network restrictions ⚠️")
# client = MongitaClientDisk(host=os.path.join(BASE_DIR, ".local_db"))
# class LocalMongo:
#     db = client.bug_tracker_db
# mongo = LocalMongo()

# MIGRATION: Switched to Real MongoDB (PyMongo)
mongo = PyMongo(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ---------------- MIDDLEWARE ----------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or session['user']['role'] != 'Admin':
            flash("Access denied: Admins only", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or session['user']['role'] not in ['Admin', 'Manager']:
            flash("Access denied: Managers only", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ---------------- ROUTES ----------------

@app.route("/")
def landing():
    if 'user' in session:
        role = session['user']['role']
        if role == 'Admin': return redirect(url_for('admin_dashboard'))
        if role == 'Manager': return redirect(url_for('manager_dashboard'))
        return redirect(url_for('developer_dashboard'))
    return render_template("landing.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role", "Developer")
        
        if not username or not password:
            flash("Missing fields", "danger")
            return redirect(url_for('signup'))

        if mongo.db.users.find_one({"username": username}):
            flash("User already exists", "danger")
            return redirect(url_for('signup'))

        user_data = {
            "username": username,
            "password": generate_password_hash(password),
            "role": role,
            "created_at": datetime.datetime.utcnow(),
            "status": "Active" if role == "Developer" else "Pending" # Managers need approval
        }
        
        mongo.db.users.insert_one(user_data)
        
        if role != "Developer":
            flash("Account created! Please wait for Admin approval.", "info")
            return redirect(url_for('login'))
            
        flash("Account created! Please login.", "success")
        return redirect(url_for("login"))
        
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = mongo.db.users.find_one({"username": request.form["username"]})
        if user and check_password_hash(user["password"], request.form["password"]):
            if user.get("status") == "Pending":
                flash("Your account is pending approval.", "warning")
                return redirect(url_for('login'))
                
            session["user"] = {
                "username": user["username"],
                "role": user["role"],
                "id": str(user["_id"])
            }
            
            if user["role"] == "Admin": return redirect(url_for('admin_dashboard'))
            if user["role"] == "Manager": return redirect(url_for('manager_dashboard'))
            return redirect(url_for('developer_dashboard'))

        flash("Invalid credentials", "danger")
        return redirect(url_for('login'))

    return render_template("login.html")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        print(f"DEBUG: Attempting Admin Login for user: {username}")
        
        user = mongo.db.users.find_one({"username": username})
        
        if user:
            print(f"DEBUG: User found: {user['username']}, Role: {user.get('role')}")
            is_valid = check_password_hash(user["password"], password)
            print(f"DEBUG: Password Valid: {is_valid}")
            
            if is_valid:
                if user["role"] != "Admin":
                    flash("Access Denied. This portal is for Admins only.", "danger")
                    return redirect(url_for('admin_login'))
                    
                session["user"] = {
                    "username": user["username"],
                    "role": user["role"],
                    "id": str(user["_id"])
                }
                return redirect(url_for('admin_dashboard'))
        else:
            print("DEBUG: User not found in database.")

        flash("Invalid admin credentials", "danger")
        return redirect(url_for('admin_login'))

    return render_template("admin_login.html")

@app.route("/logout")
def logout():
    # Check if user was admin before clearing session
    is_admin = False
    if 'user' in session and session['user'].get('role') == 'Admin':
        is_admin = True
        
    session.clear()
    
    if is_admin:
        return redirect(url_for('admin_login'))
    return redirect(url_for('login'))

# ---------------- DASHBOARDS ----------------

@app.route("/admin")
@admin_required
def admin_dashboard():
    # Mock stats for demonstration if DB is empty
    total_users = mongo.db.users.count_documents({})
    total_bugs = mongo.db.bugs.count_documents({})
    pending_managers = mongo.db.users.count_documents({"role": "Manager", "status": "Pending"})
    
    pending_managers_list = list(mongo.db.users.find({"role": "Manager", "status": "Pending"}))
    
    stats = {
        "total_users": total_users if total_users > 0 else 12,
        "total_bugs": total_bugs if total_bugs > 0 else 45,
        "pending_managers": pending_managers
    }
    return render_template("admin_dashboard.html", stats=stats, pending_managers=pending_managers_list)

@app.route("/admin/approve/<user_id>")
@admin_required
def approve_manager(user_id):
    mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"status": "Active"}})
    flash("User approved successfully!", "success")
    # Redirect back to where the request came from, or default to dashboard
    next_page = request.args.get('next')
    if next_page == 'admin_users':
        return redirect(url_for('admin_users'))
    return redirect(url_for('admin_dashboard'))

@app.route("/admin/delete_user/<user_id>", methods=["POST"])
@admin_required
def delete_user(user_id):
    mongo.db.users.delete_one({"_id": ObjectId(user_id)})
    flash("User deleted successfully!", "success")
    return redirect(url_for('admin_users'))

@app.route("/admin/users")
@admin_required
def admin_users():
    users = list(mongo.db.users.find())
    return render_template("admin_users.html", users=users)

@app.route("/admin/bugs")
@admin_required
def admin_bugs():
    bugs = list(mongo.db.bugs.find())
    return render_template("admin_bugs.html", bugs=bugs)

@app.route("/admin/reports")
@admin_required
def admin_reports():
    return render_template("admin_reports.html")

@app.route("/manager")
@manager_required
def manager_dashboard():
    # Fetch real data
    developers = list(mongo.db.users.find({"role": "Developer"}))
    bugs = list(mongo.db.bugs.find({}))
    
    # Mock Sprints
    sprints = [
        {"name": "Sprint 24", "status": "Active", "deadline": "2026-02-20", "tasks": 12},
        {"name": "Sprint 25", "status": "Planning", "deadline": "2026-03-05", "tasks": 0}
    ]
    
    stats = {
        "team_bugs": mongo.db.bugs.count_documents({}),
        "pending_review": mongo.db.bugs.count_documents({"status": "Open", "priority": "High"}), # Mock metric
        "critical_bugs": mongo.db.bugs.count_documents({"priority": "Critical"}),
        "resolved_week": 15 # Mock
    }
    
    return render_template("manager_dashboard.html", stats=stats, developers=developers, bugs=bugs, sprints=sprints)

@app.route("/developer")
@login_required
def developer_dashboard():
    # Get bugs for current user
    user_bugs = list(mongo.db.bugs.find({"reported_by": session['user']['username']}))
    
    # Sort bugs by date (newest first)
    user_bugs.sort(key=lambda x: x.get('created_at', datetime.datetime.min), reverse=True)

    # Active bugs: Open or In Progress
    active_bugs = [b for b in user_bugs if b.get('status') not in ['Resolved', 'Closed']]
    
    # History: ALL bugs reported by the user (as per user request)
    history_bugs = user_bugs
    
    return render_template("developer_dashboard.html", active_bugs=active_bugs, history_bugs=history_bugs)

@app.route("/api/bug/update/<bug_id>", methods=["POST"])
@login_required
def update_bug_status(bug_id):
    new_status = request.form.get("status")
    
    if new_status:
        mongo.db.bugs.update_one(
            {"_id": ObjectId(bug_id)},
            {"$set": {"status": new_status, "updated_at": datetime.datetime.utcnow()}}
        )
        flash(f"Bug status updated to {new_status}", "success")
    
    return redirect(url_for('developer_dashboard'))

@app.route("/api/predict", methods=["POST"])
@login_required
def predict_bug():
    data = request.json
    title = data.get("title", "")
    description = data.get("description", "")
    
    if predict_priority_and_type:
        priority, bug_type = predict_priority_and_type(title, description)
    else:
        # Fallback if model not loaded
        priority = "Medium"
        bug_type = "Bug"
        
    return jsonify({"priority": priority, "type": bug_type})

@app.route("/api/bug/submit", methods=["POST"])
@login_required
def submit_bug():
    try:
        title = request.form.get("title")
        description = request.form.get("description")
        
        if not title or not description:
            flash("Title and Description are required!", "danger")
            return redirect(url_for('developer_dashboard'))

        # Prepare attachment
        attachment_filename = None
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and file.filename != '':
                filename = secure_filename(f"{datetime.datetime.now().timestamp()}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                attachment_filename = filename

        # AI Prediction (Recalculate or trust frontend? Let's recalculate for safety/accuracy)
        priority = "Medium"
        bug_type = "Bug"
        if predict_priority_and_type:
            priority, bug_type = predict_priority_and_type(title, description)

        bug_data = {
            "title": title,
            "description": description,
            "priority": priority,
            "type": bug_type,
            "status": "Open",
            "reported_by": session['user']['username'],
            "created_at": datetime.datetime.utcnow(),
            "attachment": attachment_filename
        }
        
        mongo.db.bugs.insert_one(bug_data)
        flash("Bug reported successfully!", "success")
    except Exception as e:
        flash(f"Error submitting bug: {str(e)}", "danger")
        
    return redirect(url_for('developer_dashboard'))

@app.route("/admin/bug/<bug_id>")
@manager_required # Managers can also View
def view_bug(bug_id):
    bug = mongo.db.bugs.find_one({"_id": ObjectId(bug_id)})
    if not bug:
        flash("Bug not found", "danger")
        return redirect(url_for('admin_dashboard'))
    return render_template("bug_details.html", bug=bug)

@app.route("/admin/bug/delete/<bug_id>", methods=["POST"])
@admin_required
def delete_bug(bug_id):
    mongo.db.bugs.delete_one({"_id": ObjectId(bug_id)})
    flash("Bug deleted successfully!", "success")
    return redirect(url_for('admin_bugs'))

@app.route("/admin/export/csv")
@admin_required
def export_csv():
    import csv
    from io import StringIO
    from flask import Response

    bugs = list(mongo.db.bugs.find())
    
    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['ID', 'Title', 'Description', 'Priority', 'Type', 'Status', 'Reported By', 'Created At'])
    
    # Rows
    for bug in bugs:
        writer.writerow([
            str(bug.get('_id')),
            bug.get('title'),
            bug.get('description'),
            bug.get('priority'),
            bug.get('type'),
            bug.get('status'),
            bug.get('reported_by'),
            bug.get('created_at')
        ])
        
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=bug_report.csv"}
    )

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return flask.send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/create-admin")
def create_admin():
    existing_admin = mongo.db.users.find_one({"role": "Admin"})
    
    admin_data = {
        "username": "Ganesh",
        "password": generate_password_hash("Ganesh@535221"),
        "role": "Admin",
        "status": "Active",
        "created_at": datetime.datetime.utcnow()
    }

    if existing_admin:
        mongo.db.users.update_one({"_id": existing_admin["_id"]}, {"$set": admin_data})
        return "Admin (Ganesh) updated successfully"
    else:
        mongo.db.users.insert_one(admin_data)
        return "Admin (Ganesh) created successfully"

if __name__ == "__main__":
    app.run(debug=True)
