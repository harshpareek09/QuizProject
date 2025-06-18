# This file is the entry point of your backend Flask application.
# It sets up the app, registers routes, and starts the server.

from flask import Flask, render_template, session, redirect
from db_config import get_db_connection
from routes.student_routes import student_bp
from routes.teacher_routes import teacher_bp  # Import blueprint

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'supersecretkey@123'  # Secret key for session handling


# ✅ Health check route to test DB connection
@app.route('/')
def home():
    try:
        conn = get_db_connection()
        if conn.is_connected():
            return "✅ Database connected successfully!"
    except Exception as e:
        return f"❌ Connection failed: {e}"


# ✅ Teacher login page
@app.route('/teacher-login')
def teacher_login():
    return render_template("teacherlogin.html")


# ✅ Student login page
@app.route('/student-login')
def student_login():
    return render_template("studentlogin.html")


# ✅ Register API blueprints
app.register_blueprint(student_bp, url_prefix='/student')
app.register_blueprint(teacher_bp, url_prefix='/teacher')


# ✅ Teacher dashboard (after login)
@app.route('/teacher-dashboard')
def teacher_dashboard():
    if 'teacher_name' not in session:
        return redirect('/teacher-login')
    
    return render_template('dashboard.html', teacher_name=session['teacher_name'])


# ✅ Quiz editing page (add/edit/delete questions)
@app.route('/edit-quiz/<int:quiz_id>')
def edit_quiz_ui(quiz_id):
    if 'teacher_id' not in session:
        return redirect('/teacher-login')
    
    return render_template("edit_questions.html", quiz_id=quiz_id)


# ✅ View results of a quiz
@app.route('/view-result/<int:quiz_id>')
def view_result_ui(quiz_id):
    if 'teacher_id' not in session:
        return redirect('/teacher-login')
    
    return render_template("results.html", quiz_id=quiz_id)


# ✅ Page to create new quiz (enter quiz title)
@app.route('/create-quiz')
def create_quiz_ui():
    if 'teacher_id' not in session:
        return redirect('/teacher-login')
    
    return render_template("create_quiz.html", teacher_name=session['teacher_name'])


# ✅ Final quiz success page with shareable student link
@app.route('/quiz-success/<int:quiz_id>')
def quiz_success(quiz_id):
    if 'teacher_id' not in session:
        return redirect('/teacher-login')
    
    return render_template("quiz_success.html", quiz_id=quiz_id)


# ✅ Start Flask development server
if __name__ == '__main__':
    print("🚀 Starting Flask server at http://127.0.0.1:5000/")
    app.run(debug=True)
