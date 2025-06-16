from flask import Blueprint, request, jsonify
from db_config import get_db_connection

student_bp = Blueprint('student', __name__)

# STUDENT LOGIN
@student_bp.route('/login', methods=['POST'])
def student_login():
    try:
        data = request.get_json()
        email = data.get('email')
        full_name = data.get('full_name')
        course = data.get('course')

        # ✅ Step 1: Input Validation — All fields required
        if not email or not full_name or not course:
            return jsonify({
                'status': 'error',
                'message': 'All fields (email, full_name, course) are required.'
            }), 400

        # ✅ Step 2: DB Connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # ✅ Step 3: Verify student from database
        query = "SELECT * FROM students WHERE email = %s AND full_name = %s AND course = %s"
        cursor.execute(query, (email, full_name, course))
        student = cursor.fetchone()

        # ✅ Step 4: Send appropriate response
        if student:
            return jsonify({'status': 'success', 'message': 'Login successful'})
        else:
            return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401

    except Exception as e:
        # ✅ Step 5: Handle unexpected server error
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500

    finally:
        # ✅ Step 6: Close DB connection
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()


# ✅ GET route to fetch quiz questions (without correct_option)
@student_bp.route('/quiz/<int:quiz_id>', methods=['GET'])
def get_quiz_questions(quiz_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch all questions of the given quiz, without correct_option
        query = """
            SELECT question_id, question_text, option1, option2, option3, option4
            FROM questions
            WHERE quiz_id = %s
        """
        cursor.execute(query, (quiz_id,))
        questions = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({'success': True, 'questions': questions}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


# Student submits response for a question
@student_bp.route('/submit-response', methods=['POST'])
def submit_response():
    data = request.get_json()

    student_email = data.get('student_email')
    quiz_id = data.get('quiz_id')
    question_id = data.get('question_id')
    selected_option = data.get('selected_option')

    # ✅ Validate input
    if not all([student_email, quiz_id, question_id, selected_option]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 🔍 Get the correct answer for the question
        cursor.execute("SELECT correct_option FROM questions WHERE question_id = %s", (question_id,))
        correct_data = cursor.fetchone()

        if not correct_data:
            return jsonify({'success': False, 'message': 'Invalid question ID'}), 404

        # ✅ Compare selected option with correct one
        correct_option = correct_data['correct_option']
        is_correct = (selected_option == correct_option)

        # 💾 Insert into responses table
        insert_query = """
            INSERT INTO responses (quiz_id, student_email, question_id, selected_option, is_correct)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            quiz_id, student_email, question_id, selected_option, is_correct
        ))
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


# 🚨 Route to report a cheating violation
@student_bp.route('/violation', methods=['POST'])
def report_violation():
    # Step 1: Get data from frontend
    data = request.get_json()

    student_email = data.get('student_email')  # Email of student
    quiz_id = data.get('quiz_id')              # Quiz ID
    reason = data.get('reason')                # Reason for violation (e.g., tab switch)

    # Step 2: Check for missing fields
    if not all([student_email, quiz_id, reason]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    try:
        # Step 3: Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Step 4: Insert the violation into the violations table
        insert_query = """
            INSERT INTO violations (student_email, quiz_id, reason)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (student_email, quiz_id, reason))
        conn.commit()

        # Step 5: Close connection
        cursor.close()
        conn.close()

        # Step 6: Return success response
        return jsonify({'success': True, 'message': 'Violation recorded'}), 201

    except Exception as e:
        # Step 7: Handle errors
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


# ✅ Route for final quiz submission and result calculation
@student_bp.route('/final-submit', methods=['POST'])
def final_submit():
    data = request.get_json()

    student_email = data.get('student_email')
    quiz_id = data.get('quiz_id')

    # Step 1: Validate input
    if not student_email or not quiz_id:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Step 2: Check if cheating was detected
        cursor.execute("SELECT reason FROM violations WHERE student_email = %s AND quiz_id = %s",
                       (student_email, quiz_id))
        violation = cursor.fetchone()

        cheating_detected = violation is not None
        reason = violation['reason'] if violation else "No cheating detected"

        # Step 3: Count correct answers from responses
        cursor.execute("""
            SELECT COUNT(*) AS correct_count 
            FROM responses 
            WHERE student_email = %s AND quiz_id = %s AND is_correct = 1
        """, (student_email, quiz_id))
        correct_count = cursor.fetchone()['correct_count']

        # Step 4: Set total score = 0 if cheated, otherwise correct answers
        total_score = 0 if cheating_detected else correct_count

        # Step 5: Insert final result into final_results table
        insert_query = """
            INSERT INTO final_results (student_email, quiz_id, total_score, cheating_detected, reason)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            student_email, quiz_id, total_score, cheating_detected, reason
        ))

        conn.commit()
        cursor.close()
        conn.close()

        # Step 6: Return result response
        return jsonify({
            'success': True,
            'message': 'Result submitted successfully',
            'score': total_score,
            'cheating_detected': cheating_detected,
            'reason': reason
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# ✅ Get student's final result for a specific quiz
@student_bp.route('/result/<int:quiz_id>/<student_email>', methods=['GET'])
def get_student_result(quiz_id, student_email):
    try:
        # Step 1: Connect to DB
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Step 2: Get quiz title for reference
        cursor.execute("SELECT title FROM quizzes WHERE quiz_id = %s", (quiz_id,))
        quiz = cursor.fetchone()

        # Step 3: Fetch result from final_results
        cursor.execute("""
            SELECT total_score, cheating_detected, reason 
            FROM final_results 
            WHERE quiz_id = %s AND student_email = %s
        """, (quiz_id, student_email))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        # Step 4: Check if result exists
        if not result:
            return jsonify({'success': False, 'message': 'Result not found'}), 404

        # Step 5: Return structured result
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
