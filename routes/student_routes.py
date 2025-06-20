from flask import Blueprint, request, jsonify, render_template
from db_config import get_db_connection

student_bp = Blueprint('student', __name__)

# ✅ Shared Link → Student Login Page
@student_bp.route('/attempt-quiz/<int:quiz_id>', methods=['GET'])
def attempt_quiz(quiz_id):
    return render_template('studentlogin.html', quiz_id=quiz_id)

# ✅ Student Login + Redirect Handler
@student_bp.route('/login-quiz', methods=['POST'])
def login_quiz():
    data = request.get_json()
    email = data.get("email")
    name = data.get("full_name")
    course = data.get("course")
    quiz_id = data.get("quiz_id")

    if not all([email, name, course, quiz_id]):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Already attempted
        cursor.execute("SELECT * FROM final_results WHERE student_email = %s AND quiz_id = %s", (email, quiz_id))
        result = cursor.fetchone()
        if result:
            return jsonify({
                "status": "success",
                "already_attempted": True,
                "redirect_url": f"/student/result/{quiz_id}?email={email}"
            }), 200

        # New student? Add
        cursor.execute("SELECT * FROM students WHERE email = %s", (email,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO students (email, name, course) VALUES (%s, %s, %s)", (email, name, course))
            conn.commit()

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"status": "error", "message": "Internal server error"}), 500

    finally:
        cursor.close()
        conn.close()

# ✅ Render Start Quiz Page
@student_bp.route('/start-quiz/<int:quiz_id>', methods=['GET'])
def start_quiz(quiz_id):
    return render_template('start_quiz.html', quiz_id=quiz_id)

# ✅ Get Questions
@student_bp.route('/quiz/<int:quiz_id>', methods=['GET'])
def get_quiz_questions(quiz_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT question_id, question_text, option1, option2, option3, option4
            FROM questions WHERE quiz_id = %s
        """, (quiz_id,))
        questions = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'questions': questions}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# ✅ Save Response (FIXED)
@student_bp.route('/submit-response', methods=['POST'])
def submit_response():
    data = request.get_json()
    student_email = data.get('student_email')
    quiz_id = data.get('quiz_id')
    question_id = data.get('question_id')
    selected_option = data.get('selected_option')

    if not all([student_email, quiz_id, question_id, selected_option]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT correct_option FROM questions WHERE question_id = %s", (question_id,))
        correct_data = cursor.fetchone()

        if not correct_data:
            return jsonify({'success': False, 'message': 'Invalid question ID'}), 404

        correct_option = correct_data['correct_option']
        selected_option = int(selected_option)
        is_correct = (selected_option == int(correct_option))

        cursor.execute("""
            INSERT INTO responses (quiz_id, student_email, question_id, selected_option, is_correct)
            VALUES (%s, %s, %s, %s, %s)
        """, (quiz_id, student_email, question_id, selected_option, is_correct))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Response submitted successfully',
            'is_correct': is_correct
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# ✅ Report Cheating
@student_bp.route('/violation', methods=['POST'])
def report_violation():
    data = request.get_json()
    student_email = data.get('student_email')
    quiz_id = data.get('quiz_id')
    reason = data.get('reason')

    if not all([student_email, quiz_id, reason]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO violations (student_email, quiz_id, reason)
            VALUES (%s, %s, %s)
        """, (student_email, quiz_id, reason))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Violation recorded'}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# ✅ Final Submit and Scoring
@student_bp.route('/final-submit', methods=['POST'])
def final_submit():
    data = request.get_json()
    student_email = data.get('student_email')
    quiz_id = data.get('quiz_id')

    if not student_email or not quiz_id:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT reason FROM violations WHERE student_email = %s AND quiz_id = %s",
                       (student_email, quiz_id))
        violation = cursor.fetchone()

        cheating_detected = violation is not None
        reason = violation['reason'] if violation else "No cheating detected"

        cursor.execute("""
            SELECT COUNT(*) AS correct_count 
            FROM responses 
            WHERE student_email = %s AND quiz_id = %s AND is_correct = 1
        """, (student_email, quiz_id))
        correct_count = cursor.fetchone()['correct_count']

        total_score = 0 if cheating_detected else correct_count

        cursor.execute("""
            INSERT INTO final_results (student_email, quiz_id, total_score, cheating_detected, reason)
            VALUES (%s, %s, %s, %s, %s)
        """, (student_email, quiz_id, total_score, cheating_detected, reason))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Result submitted successfully',
            'score': total_score,
            'cheating_detected': cheating_detected,
            'reason': reason
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# ✅ Get Result
@student_bp.route('/result/<int:quiz_id>/<student_email>', methods=['GET'])
def get_student_result(quiz_id, student_email):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT title FROM quizzes WHERE quiz_id = %s", (quiz_id,))
        quiz = cursor.fetchone()

        cursor.execute("""
            SELECT total_score, cheating_detected, reason 
            FROM final_results 
            WHERE quiz_id = %s AND student_email = %s
        """, (quiz_id, student_email))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if not result:
            return jsonify({'success': False, 'message': 'Result not found'}), 404

        return jsonify({
            'success': True,
            'quiz_title': quiz['title'] if quiz else 'Unknown',
            'student_email': student_email,
            'score': result['total_score'],
            'cheating_detected': result['cheating_detected'],
            'reason': result['reason']
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# ✅ Serve result UI page (after final submit)
@student_bp.route('/view-result/<int:quiz_id>', methods=['GET'])
def view_result_page(quiz_id):
    student_email = request.args.get("email")
    if not student_email:
        return "Invalid Request: Email required", 400
    return render_template("student_result.html", quiz_id=quiz_id, student_email=student_email)
