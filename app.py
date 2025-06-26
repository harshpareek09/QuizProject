from flask import Flask, render_template, session, redirect
from db_config import get_db_connection
from routes.student_routes import student_bp
from routes.teacher_routes import teacher_bp

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'supersecretkey@123'

# ✅ Root Route with Login Options
@app.route('/')
def home():
    return render_template("index.html")

# ✅ Student login via shared link fallback
@app.route('/student-login')
def student_login():
    return render_template("studentlogin.html")

# ✅ Teacher login page
@app.route('/teacher-login')
def teacher_login():
    return render_template("teacherlogin.html")

# ✅ Register Blueprints
app.register_blueprint(student_bp, url_prefix='/student')
app.register_blueprint(teacher_bp, url_prefix='/teacher')

# ✅ Teacher dashboard
@app.route('/teacher-dashboard')
def teacher_dashboard():
    if 'teacher_name' not in session:
        return redirect('/teacher-login')
    return render_template('dashboard.html', teacher_name=session['teacher_name'])

# ✅ Quiz editing page
@app.route('/edit-quiz/<int:quiz_id>')
def edit_quiz_ui(quiz_id):
    if 'teacher_id' not in session:
        return redirect('/teacher-login')
    return render_template("edit_questions.html", quiz_id=quiz_id)

# ✅ View quiz results
@app.route('/view-result/<int:quiz_id>')
def view_result_ui(quiz_id):
    if 'teacher_id' not in session:
        return redirect('/teacher-login')
    return render_template("results.html", quiz_id=quiz_id)

# ✅ Create new quiz page
@app.route('/create-quiz')
def create_quiz_ui():
    if 'teacher_id' not in session:
        return redirect('/teacher-login')
    return render_template("create_quiz.html", teacher_name=session['teacher_name'])

# ✅ Final quiz success page
@app.route('/quiz-success/<int:quiz_id>')
def quiz_success(quiz_id):
    if 'teacher_id' not in session:
        return redirect('/teacher-login')
    return render_template("quiz_success.html", quiz_id=quiz_id)

# # ✅ Start Server
# if __name__ == '__main__':
#     print("\n🚀 Starting Flask server at http://127.0.0.1:5000/")
#     app.run(debug=True)

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Server running on http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port)
