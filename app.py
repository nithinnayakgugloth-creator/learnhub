import os
from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
from bson.objectid import ObjectId
import hashlib

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Production configuration
app.secret_key = os.environ.get('SECRET_KEY', 'learnhub-secret-key-change-in-production')

# MongoDB connection with connection pooling for production
# For local development: mongodb://localhost:27017/
# For MongoDB Atlas: mongodb+srv://...
mongo_uri = os.environ.get('DATABASE_URL', 'mongodb://localhost:27017/')

# Connection pooling settings for production
client = MongoClient(
    mongo_uri,
    maxPoolSize=50,
    minPoolSize=10,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=10000
)

db = client.get_default_database()
if 'learnhub' not in client.list_database_names():
    # Create database if it doesn't exist (for local dev)
    db = client['learnhub']

users_col = db["users"]
courses_col = db["courses"]
enrollments_col = db["enrollments"]

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ================= HEALTH CHECK =================
@app.route("/health")
def health():
    return {'status': 'healthy'}, 200

# ================= SEED COURSES =================
@app.route("/create_tables")
def create_tables():
    if courses_col.count_documents({}) == 0:
        courses_col.insert_many([
            {"title": "Python Programming", "description": "Learn Python from basics to advanced OOP.", "icon": "🐍"},
            {"title": "Java Development",   "description": "Master Java and Object-Oriented Programming.", "icon": "☕"},
            {"title": "Web Development",    "description": "Build websites with HTML, CSS, and JavaScript.", "icon": "🌐"},
            {"title": "Data Science",       "description": "Analyze data and build ML models with Python.", "icon": "📊"},
        ])
    return "✅ Database ready! Go to http://127.0.0.1:5000"

# ================= HOME =================
@app.route("/")
def home():
    return render_template("index.html")

# ================= SIGNUP =================
@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None
    if request.method == "POST":
        email    = request.form["email"]
        password = hash_password(request.form["password"])
        if users_col.find_one({"email": email}):
            error = "Email already registered. Please login."
        else:
            users_col.insert_one({"email": email, "password": password, "role": "user"})
            return redirect("/login")
    return render_template("signup.html", error=error)

# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email    = request.form["email"]
        password = hash_password(request.form["password"])
        user = users_col.find_one({"email": email, "password": password})
        if user:
            session["user_id"] = str(user["_id"])
            session["role"]    = user.get("role", "user")
            session["email"]   = email
            return redirect("/dashboard")
        else:
            error = "Invalid email or password."
    return render_template("login.html", error=error)

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= COURSES =================
@app.route("/courses")
def courses():
    all_courses = list(courses_col.find())
    enrolled_ids = []
    if "user_id" in session:
        enrs = enrollments_col.find({"user_id": session["user_id"]})
        enrolled_ids = [e["course_id"] for e in enrs]
    return render_template("courses.html", courses=all_courses, enrolled_ids=enrolled_ids)

# ================= ENROLL =================
@app.route("/enroll/<course_id>")
def enroll(course_id):
    if "user_id" not in session:
        return redirect("/login")
    existing = enrollments_col.find_one({"user_id": session["user_id"], "course_id": course_id})
    if not existing:
        enrollments_col.insert_one({"user_id": session["user_id"], "course_id": course_id})
    return redirect("/dashboard")

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    enrs = enrollments_col.find({"user_id": session["user_id"]})
    enrolled_courses = []
    for e in enrs:
        course = courses_col.find_one({"_id": ObjectId(e["course_id"])})
        if course:
            enrolled_courses.append(course)
    return render_template("dashboard.html", courses=enrolled_courses, email=session.get("email", ""))

# ================= PYTHON COURSE =================
@app.route("/python")
def python_course():
    return render_template("python.html")

# ================= JAVA COURSE =================
@app.route("/java")
def java_course():
    return render_template("java.html")

# ================= QUIZ =================
@app.route("/quiz")
def quiz():
    return render_template("quiz.html")

# ================= ADMIN =================
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "role" not in session or session["role"] != "admin":
        return redirect("/")
    if request.method == "POST":
        courses_col.insert_one({
            "title":       request.form["title"],
            "description": request.form["description"],
            "icon":        request.form.get("icon", "📚")
        })
        return redirect("/courses")
    all_users   = list(users_col.find())
    course_count = courses_col.count_documents({})
    enrollment_count = enrollments_col.count_documents({})
    return render_template("admin.html", users=all_users, course_count=course_count, enrollment_count=enrollment_count)

if __name__ == "__main__":
    # Run with debug=True only in development
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
