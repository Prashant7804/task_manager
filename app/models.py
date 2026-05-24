from . import db
from flask_login import UserMixin
from datetime import datetime

# User model for authentication and task ownership
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email    = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    reset_token = db.Column(db.String(100), nullable=True)
    tasks    = db.relationship('Task', backref='owner', lazy=True)

# Task model for representing individual tasks
class Task(db.Model):
    __tablename__ = 'tasks'
    id           = db.Column(db.Integer, primary_key=True)
    title        = db.Column(db.String(120), nullable=False)
    description  = db.Column(db.Text)
    priority     = db.Column(db.String(20), default='medium')  # low / medium / high
    status       = db.Column(db.String(20), default='pending') # pending / completed
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

