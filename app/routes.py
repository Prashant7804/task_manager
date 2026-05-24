# this file contains all the routes for the Flask application,
# including user authentication, task management APIs, and analytics API. It also includes a helper function to broadcast task updates via WebSockets.
# The routes are organized using a Blueprint for better modularity. Each route is decorated with appropriate HTTP methods and login requirements where necessary.
# The analytics route computes task statistics using pandas for data manipulation.

from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from . import db, bcrypt, login_manager
from .models import User, Task
import secrets

main = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home Page
@main.route('/')
@login_required
def index():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_date.desc()).all()
    return render_template('index.html', tasks=tasks)

# Register
@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form.get('username')
        email    = request.form.get('email')
        password = request.form.get('password')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('main.register'))
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html')

# Login page
@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        email    = request.form.get('email')
        password = request.form.get('password')
        user     = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html')

# Logout
@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

# Forgot Password
@main.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user  = User.query.filter_by(email=email).first()
        if user:
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            db.session.commit()
            reset_url = url_for('main.reset_password', token=token, _external=True)
            flash(f'Reset link (copy this): {reset_url}', 'success')
        else:
            flash('No account found with that email.', 'danger')
    return render_template('forgot_password.html')

# Reset Password 
@main.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()
    if not user:
        flash('Invalid or expired reset link.', 'danger')
        return redirect(url_for('main.login'))
    if request.method == 'POST':
        password = request.form.get('password')
        confirm  = request.form.get('confirm_password')
        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('reset_password.html')
        user.password    = bcrypt.generate_password_hash(password).decode('utf-8')
        user.reset_token = None
        db.session.commit()
        flash('Password updated! Please log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('reset_password.html')


# task management APIs
# these routes handle CRUD operations for tasks. Each route checks for user authentication and ensures that users can only access their own tasks.
# After any modification to tasks, a WebSocket broadcast is sent to update the client in real-time.

# get all tasks for the current user
@main.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_date.desc()).all()
    return jsonify([{
        'id':           t.id,
        'title':        t.title,
        'description':  t.description,
        'priority':     t.priority,
        'status':       t.status,
        'created_date': t.created_date.strftime('%Y-%m-%d %H:%M')
    } for t in tasks])

# add a new task for the current user
@main.route('/api/tasks', methods=['POST'])
@login_required
def add_task():
    data = request.get_json()
    if not data or not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    task = Task(
        title       = data.get('title'),
        description = data.get('description', ''),
        priority    = data.get('priority', 'medium'),
        status      = data.get('status', 'pending'),
        user_id     = current_user.id
    )
    db.session.add(task)
    db.session.commit()
    broadcast_task_update(current_user.id)
    return jsonify({'message': 'Task added', 'id': task.id}), 201

# update an existing task for the current user
@main.route('/api/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    data = request.get_json()
    task.title       = data.get('title',       task.title)
    task.description = data.get('description', task.description)
    task.priority    = data.get('priority',    task.priority)
    task.status      = data.get('status',      task.status)
    db.session.commit()
    broadcast_task_update(current_user.id)
    return jsonify({'message': 'Task updated'})

# delete a task for the current user
@main.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    db.session.delete(task)
    db.session.commit()
    broadcast_task_update(current_user.id)
    return jsonify({'message': 'Task deleted'})


# analytics API
# this route computes various statistics about the user's tasks, such as total count, completion rate,
# and distribution by priority. It uses pandas for data manipulation to efficiently calculate these metrics and returns the results as JSON for use in the analytics dashboard.
# If the user has no tasks, it returns default values to avoid division by zero errors.
from flask import current_app
import pandas as pd
import numpy as np

@main.route('/api/analytics', methods=['GET'])
@login_required
def analytics():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    if not tasks:
        return jsonify({
            'total': 0, 'completed': 0, 'pending': 0,
            'completion_rate': 0,
            'by_priority': {'low': 0, 'medium': 0, 'high': 0}
        })

    df = pd.DataFrame([{
        'status':   t.status,
        'priority': t.priority,
        'created':  t.created_date
    } for t in tasks])

    total     = len(df)
    completed = int((df['status'] == 'completed').sum())
    pending   = int((df['status'] == 'pending').sum())
    rate      = round(float(np.divide(completed, total) * 100), 1)

    by_priority = df.groupby('priority').size().reindex(
        ['low', 'medium', 'high'], fill_value=0
    ).to_dict()
    by_priority = {k: int(v) for k, v in by_priority.items()}

    return jsonify({
        'total':           total,
        'completed':       completed,
        'pending':         pending,
        'completion_rate': rate,
        'by_priority':     by_priority
    })

# helper function to broadcast task updates via WebSockets
from . import socketio
from flask_socketio import emit

# this function is called after any task modification (add, update, delete) to notify the client in real-time about the changes. It emits a 'tasks_updated' event to the specific user's room, allowing the frontend to refresh the task list without needing a full page reload.
def broadcast_task_update(user_id):
    socketio.emit('tasks_updated', {'user_id': user_id}, room=f'user_{user_id}')

# Analytics page route
@main.route('/analytics')
@login_required
def analytics_page():
    return render_template('analytics.html')
