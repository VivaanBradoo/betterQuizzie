from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    data = db.Column(db.JSON, nullable=False)  # Stores questions and options
    taken_count = db.Column(db.Integer, default=0)  # How many times the quiz was taken

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    user_name = db.Column(db.String(150), nullable=False)
