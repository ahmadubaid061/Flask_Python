from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    # If someone's already logged in and lands on '/', send them
    # straight to their dashboard instead of the marketing page
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))
    return render_template('home.html')