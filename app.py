from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Quiz, Result
from config import Config
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.before_request
def create_tables():
    try:
        db.create_all()
    except SQLAlchemy.exc.ProgrammingError:
        print("Table already exists, skipping creation.")

@app.route('/')
def home():
    quizzes = Quiz.query.all()  
    return render_template('home.html', quizzes=quizzes)

@app.route('/create-quiz', methods=['GET', 'POST'])
def create_quiz():
    if request.method == 'POST':
        title = request.form['title']
        questions = []

        question_counter = 1
        while f'question_{question_counter}' in request.form:
            question_text = request.form[f'question_{question_counter}']
            options = [
                request.form[f'option_{question_counter}_1'],
                request.form[f'option_{question_counter}_2'],
                request.form[f'option_{question_counter}_3'],
                request.form[f'option_{question_counter}_4']
            ]
            correct = int(request.form[f'correct_{question_counter}'])
            questions.append({
                'question': question_text,
                'options': options,
                'correct': correct
            })
            question_counter += 1

        quiz = Quiz(title=title, data=questions)
        db.session.add(quiz)
        db.session.commit()
        flash(f"Quiz created with ID: {quiz.id}", 'success')
        return redirect(url_for('home'))
    
    return render_template('create_quiz.html')

@app.route('/take-quiz/<int:quiz_id>', methods=['GET', 'POST'])
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if request.method == 'POST':
        score = 0
        for i, question in enumerate(quiz.data):
            answer = int(request.form.get(f'question_{i + 1}', 0))
            if answer == question['correct']:
                score += 1
        quiz.taken_count += 1
        result = Result(quiz_id=quiz.id, score=score, user_name=request.form['user_name'])
        db.session.add(result)
        db.session.commit()
        flash(f"Your score: {score}/{len(quiz.data)}", 'info')
        return redirect(url_for('home'))
    return render_template('take_quiz.html', quiz=quiz, enumerate=enumerate)

@app.route('/quiz-participants/<int:quiz_id>')
def quiz_participants(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    results = Result.query.filter_by(quiz_id=quiz_id).all()
    return render_template('quiz_participants.html', quiz=quiz, results=results)

@app.route('/clear-results/<int:quiz_id>', methods=['POST'])
def clear_results(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    Result.query.filter_by(quiz_id=quiz_id).delete()
    db.session.commit()
    flash(f"All participants' results for the quiz '{quiz.title}' have been cleared.", 'success')
    return redirect(url_for('quiz_participants', quiz_id=quiz_id))

@app.route('/delete_quiz/<int:quiz_id>', methods=['POST'])
def delete_quiz(quiz_id):
    try:
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return "Quiz not found", 404

        Result.query.filter_by(quiz_id=quiz_id).delete()
        db.session.delete(quiz)
        db.session.commit()
        return redirect('/')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting quiz: {e}")
        return f"An error occurred: {e}", 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
