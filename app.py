# This file is the entry point of your backend Flask application.
# It sets up the app, registers routes, and starts the server.

from flask import Flask, render_template
from db_config import get_db_connection
from routes.student_routes import student_bp
from routes.teacher_routes import teacher_bp  # ✅ Correct import

app = Flask(__name__, static_folder='static', template_folder='templates')


# ✅ Health check route to test DB connection
@app.route('/')
def home():
    try:
        conn = get_db_connection()
        if conn.is_connected():
            return "✅ Database connected successfully!"
    except Exception as e:
        return f"❌ Connection failed: {e}"

# ✅ HTML page routes (frontend login pages)
@app.route('/teacher-login')
def teacher_login():
    return render_template("teacherlogin.html")

@app.route('/student-login')
def student_login():
    return render_template("studentlogin.html")

# ✅ Register Blueprints for APIs
app.register_blueprint(student_bp, url_prefix='/student')
app.register_blueprint(teacher_bp, url_prefix='/teacher')

# ✅ Start Flask server
if __name__ == '__main__':
    print("🚀 Starting Flask server at http://127.0.0.1:5000/")
    app.run(debug=True)
