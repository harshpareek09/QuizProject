# routes/teacher_routes.py

from flask import Blueprint, request, jsonify
import mysql.connector
from db_config import get_db_connection

# Blueprint for teacher-related routes
teacher_bp = Blueprint('teacher', __name__)

# POST route for teacher login
@teacher_bp.route('/login', methods=['POST'])
def teacher_login():
    # Step 1: Extract request data
    data = request.get_json()
    teacher_id = data.get('teacher_id')
    full_name = data.get('full_name')
    password = data.get('password')

    # Step 2: Validate required fields
    if not teacher_id or not full_name or not password:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    try:
        # Step 3: Connect to the DB
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Step 4: Query to verify teacher credentials
        query = "SELECT * FROM teachers WHERE teacher_id = %s AND full_name = %s AND password = %s"
        cursor.execute(query, (teacher_id, full_name, password))
        teacher = cursor.fetchone()

        # Step 5: Close connection
        cursor.close()
        conn.close()

        # Step 6: Return appropriate response
        if teacher:
            return jsonify({'success': True, 'message': 'Login successful', 'teacher': teacher}), 200
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

    except mysql.connector.Error as err:
        return jsonify({'success': False, 'message': f'Database error: {err}'}), 500



# POST route to add a question to a quiz
@teacher_bp.route('/add-question', methods=['POST'])
def add_question():
    data = request.get_json()

    quiz_id = data.get('quiz_id')
    question_text = data.get('question_text')
    option1 = data.get('option1')
    option2 = data.get('option2')
    option3 = data.get('option3')
    option4 = data.get('option4')
    correct_option = data.get('correct_option')

    # Validate input
    if not all([quiz_id, question_text, option1, option2, option3, option4, correct_option]):
        return jsonify({'success': False, 'message': 'All fields are required'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert question into DB
        insert_query = """
            INSERT INTO questions (quiz_id, question_text, option1, option2, option3, option4, correct_option)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            quiz_id, question_text, option1, option2, option3, option4, correct_option
        ))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Question added successfully'}), 201

    except mysql.connector.Error as err:
        return jsonify({'success': False, 'message': f'Database error: {err}'}), 500


# ✅ Get all results for a specific quiz
@teacher_bp.route('/results/<int:quiz_id>', methods=['GET'])
def get_quiz_results(quiz_id):
    try:
        # Step 1: Connect to DB
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Step 2: Get quiz title
        cursor.execute("SELECT title FROM quizzes WHERE quiz_id = %s", (quiz_id,))
        quiz = cursor.fetchone()
        quiz_title = quiz['title'] if quiz else "Unknown Quiz"

        # Step 3: Fetch all results for this quiz
        cursor.execute("""
            SELECT student_email, total_score, cheating_detected, reason
            FROM final_results
            WHERE quiz_id = %s
        """, (quiz_id,))
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        # Step 4: Return results list
        return jsonify({
            'success': True,
            'quiz_id': quiz_id,
            'quiz_title': quiz_title,
            'results': results
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


# 📍 Get all quizzes created by a teacher
@teacher_bp.route('/quizzes/<teacher_id>', methods=['GET'])
def get_teacher_quizzes(teacher_id):
    try:
        # Step 1: Connect to DB
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Step 2: Fetch quizzes by this teacher
        query = "SELECT quiz_id, title, created_at FROM quizzes WHERE teacher_id = %s ORDER BY created_at DESC"
        cursor.execute(query, (teacher_id,))
        quizzes = cursor.fetchall()

        # Step 3: Close connection
        cursor.close()
        conn.close()

        # Step 4: Return quiz list
        return jsonify({'success': True, 'quizzes': quizzes}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


# 📍 Get all questions for a specific quiz
@teacher_bp.route('/questions/<int:quiz_id>', methods=['GET'])
def get_quiz_questions(quiz_id):
    try:
        # Step 1: Connect to DB
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Step 2: Fetch questions
        query = """
            SELECT question_id, question_text, option1, option2, option3, option4, correct_option
            FROM questions
            WHERE quiz_id = %s
        """
        cursor.execute(query, (quiz_id,))
        questions = cursor.fetchall()

        # Step 3: Close connection
        cursor.close()
        conn.close()

        # Step 4: Return result
        return jsonify({'success': True, 'questions': questions}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500



from flask import make_response
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# 📄 Export final results of a quiz as PDF
@teacher_bp.route('/export/<int:quiz_id>', methods=['GET'])
def export_results_pdf(quiz_id):
    try:
        # Step 1: Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Step 2: Get student result + name + course using JOIN
        query = """
            SELECT s.full_name, s.email, s.course,
                   f.total_score, f.cheating_detected, f.reason
            FROM final_results f
            JOIN students s ON f.student_email = s.email
            WHERE f.quiz_id = %s
        """
        cursor.execute(query, (quiz_id,))
        results = cursor.fetchall()

        # Step 3: Setup PDF buffer
        pdf_buffer = io.BytesIO()
        pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
        pdf.setFont("Helvetica", 12)

        # Step 4: Title
        pdf.drawString(50, 750, f"Quiz Results for Quiz ID: {quiz_id}")
        y = 720

        # Step 5: Add table rows
        for i, row in enumerate(results):
            full_name, email, course, score, cheated, reason = row
            line = f"{i+1}. {full_name} | {email} | {course} | Score: {score} | Cheated: {cheated} | Reason: {reason}"
            pdf.drawString(40, y, line)
            y -= 20
            if y < 50:
                pdf.showPage()
                y = 750

        pdf.save()
        pdf_buffer.seek(0)

        # Step 6: Return PDF as download
        response = make_response(pdf_buffer.read())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=quiz_{quiz_id}_results.pdf'
        return response

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error generating PDF: {str(e)}'}), 500

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()



#API to delete whole Quiz
@teacher_bp.route('/delete-quiz/<int:quiz_id>', methods=['DELETE'])
def delete_quiz(quiz_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # ✅ 1. Delete from responses → indirectly linked via questions
        cursor.execute("""
            DELETE responses FROM responses
            JOIN questions ON responses.question_id = questions.question_id
            WHERE questions.quiz_id = %s
        """, (quiz_id,))

        # ✅ 2. Delete from questions
        cursor.execute("DELETE FROM questions WHERE quiz_id = %s", (quiz_id,))

        # ✅ 3. Delete from violations
        cursor.execute("DELETE FROM violations WHERE quiz_id = %s", (quiz_id,))

        # ✅ 4. Delete from final_results
        cursor.execute("DELETE FROM final_results WHERE quiz_id = %s", (quiz_id,))

        # ✅ 5. Finally, delete from quizzes
        cursor.execute("DELETE FROM quizzes WHERE quiz_id = %s", (quiz_id,))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Quiz and related data deleted successfully'}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


# Delete each question
@teacher_bp.route('/delete-question/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        #  First delete responses linked to this question
        cursor.execute("DELETE FROM responses WHERE question_id = %s", (question_id,))

        #  Now delete the question
        cursor.execute("DELETE FROM questions WHERE question_id = %s", (question_id,))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Question deleted successfully'}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500



# Edit Question API
@teacher_bp.route('/update-question/<int:question_id>', methods=['PUT'])
def update_question(question_id):
    data = request.get_json()
    question_text = data.get('question_text')
    option1 = data.get('option1')
    option2 = data.get('option2')
    option3 = data.get('option3')
    option4 = data.get('option4')
    correct_option = data.get('correct_option')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            UPDATE questions
            SET question_text = %s,
                option1 = %s,
                option2 = %s,
                option3 = %s,
                option4 = %s,
                correct_option = %s
            WHERE question_id = %s
        """

        cursor.execute(query, (question_text, option1, option2, option3, option4, correct_option, question_id))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Question updated successfully'}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
