from flask import Blueprint, render_template, redirect, url_for, flash,request,session
from app.models import User
from app import db
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            flash('Login successful!', 'success')
            session['user_id'] = user.id
            return redirect(url_for('tasks.view_tasks'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists', 'danger')
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
    return render_template('register.html')