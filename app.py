from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Quiz, Result
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.before_request
def create_tables():
    db.create_all()

# Home Route
@app.route('/')
def home():
    quizzes = Quiz.query.all()  
    return render_template('home.html', quizzes=quizzes)

# Create Quiz
@app.route('/create-quiz', methods=['GET', 'POST'])
def create_quiz():
    if request.method == 'POST':
        title = request.form['title']
        questions = []

        # Loop through the dynamically added questions
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

# Take Quiz
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

# Run App
if __name__ == '__main__':
    app.run(debug=True)
