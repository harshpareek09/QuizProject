# This file is the entry point of your backend Flask application.
# It sets up the app, registers routes, and starts the server.

from flask import Flask, render_template, session, redirect
from db_config import get_db_connection
from routes.student_routes import student_bp
from routes.teacher_routes import teacher_bp  # Correct import

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'supersecretkey@123'  #  You can customize this string



#  Health check route to test DB connection
@app.route('/')
def home():
    try:
        conn = get_db_connection()
        if conn.is_connected():
            return "Database connected successfully!"
    except Exception as e:
        return f" Connection failed: {e}"

#  HTML page routes (frontend login pages)
@app.route('/teacher-login')
def teacher_login():
    return render_template("teacherlogin.html")

@app.route('/student-login')
def student_login():
    return render_template("studentlogin.html")

#  Register Blueprints for APIs
app.register_blueprint(student_bp, url_prefix='/student')
app.register_blueprint(teacher_bp, url_prefix='/teacher')



# Dasboard teacher name
@app.route('/teacher-dashboard')
def teacher_dashboard():
    # If not logged in, redirect to login page
    if 'teacher_name' not in session:
        return redirect('/teacher-login')
    
    print("Logged-in Teacher Name:", session.get('teacher_name'))

    # If logged in, render dashboard with teacher's name
    return render_template('dashboard.html', teacher_name=session['teacher_name'])

# Edit Question Route
@app.route('/edit-quiz/<int:quiz_id>')
def edit_quiz_ui(quiz_id):
    # Redirect if not logged in
    if 'teacher_id' not in session:
        return redirect('/teacher-login')
    
    # Load the edit_questions.html and pass quiz_id
    return render_template("edit_questions.html", quiz_id=quiz_id)



#  Start Flask server
if __name__ == '__main__':
    print("Starting Flask server at http://127.0.0.1:5000/")
    app.run(debug=True)
