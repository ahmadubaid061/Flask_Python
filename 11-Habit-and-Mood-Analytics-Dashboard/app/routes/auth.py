from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from urllib.parse import urlparse

from app.extensions import db
from app.models import User
from app.forms import RegisterForm, LoginForm
from app.utils.email import send_verification_email, confirm_verification_token

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(email=form.email.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()

        send_verification_email(new_user.email)
        flash('Account created! Check your email(spam folder) to verify before logging in.')
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)


@auth_bp.route('/verify/<token>')
def verify_email(token):
    email = confirm_verification_token(token)
    if email is None:
        flash('That verification link is invalid or has expired.')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email).first_or_404()
    if user.verified:
        flash('Account already verified. You can log in.')
    else:
        user.verified = True
        db.session.commit()
        flash('Email verified! You can now log in.')

    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.check_password(form.password.data):
            if not user.verified:
                flash('Please verify your email before logging in.')
                return redirect(url_for('auth.login'))

            login_user(user)
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('dashboard.home')
            return redirect(next_page)

        flash('Invalid email or password.')

    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('auth.login'))