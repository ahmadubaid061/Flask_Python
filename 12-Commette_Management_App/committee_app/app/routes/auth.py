from datetime import datetime, timedelta, timezone

from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, session, make_response
from flask_login import login_user, logout_user, current_user, login_required

from app.extensions import db
from app.models.admin import Admin
from app.models.device_token import TrustedDevice, LoginVerification
from app.forms.auth_forms import LoginForm, VerifyCodeForm, AddAdminForm
from app.utils.tokens import generate_login_code, hash_code, generate_device_token
from app.utils.email import send_login_code_email

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.strip()  # Remove any whitespace
        print(f"[DEBUG] Login attempt with username: '{username}'")
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin is None:
            print(f"[DEBUG] No admin found with username: '{username}'")
            flash("Incorrect username or password.", "error")
            return render_template("auth/login.html", form=form)
        
        print(f"[DEBUG] Admin found: {admin.username}, checking password...")
        
        if not admin.check_password(form.password.data):
            print(f"[DEBUG] Password mismatch for user: {username}")
            flash("Incorrect username or password.", "error")
            return render_template("auth/login.html", form=form)

        print(f"[DEBUG] Password verified for user: {username}")

        # Check for a trusted-device cookie matching this admin
        cookie_name = current_app.config["TRUSTED_DEVICE_COOKIE_NAME"]
        device_token = request.cookies.get(cookie_name)
        trusted = None
        if device_token:
            trusted = TrustedDevice.query.filter_by(
                admin_id=admin.id, device_token=device_token
            ).first()

        if trusted:
            print(f"[DEBUG] Trusted device found, logging in directly...")
            trusted.last_used_at = datetime.now(timezone.utc)
            db.session.commit()
            login_user(admin)
            return redirect(url_for("dashboard.index"))

        # New/unrecognized browser: issue a code and email it
        print(f"[DEBUG] New device, generating login code...")
        code = generate_login_code()
        verification = LoginVerification(
            admin_id=admin.id,
            code_hash=hash_code(code),
            expires_at=datetime.now(timezone.utc)
            + timedelta(minutes=current_app.config["LOGIN_CODE_EXPIRY_MINUTES"]),
        )
        db.session.add(verification)
        db.session.commit()

        print(f"[DEBUG] Login code generated: {code}, sending email to {admin.email}...")
        send_login_code_email(admin.email, code)

        # Stash which admin is pending verification in the server-side
        # session (not a cookie the user can tamper with)
        session["pending_admin_id"] = admin.id
        flash("A verification code has been emailed to you.", "info")
        return redirect(url_for("auth.verify"))

    return render_template("auth/login.html", form=form)


@auth_bp.route("/verify", methods=["GET", "POST"])
def verify():
    admin_id = session.get("pending_admin_id")
    if not admin_id:
        return redirect(url_for("auth.login"))

    form = VerifyCodeForm()
    if form.validate_on_submit():
        verification = (
            LoginVerification.query.filter_by(admin_id=admin_id, consumed=False)
            .order_by(LoginVerification.created_at.desc())
            .first()
        )

        if verification is None or not verification.is_valid():
            flash("That code has expired. Please log in again to get a new one.", "error")
            session.pop("pending_admin_id", None)
            return redirect(url_for("auth.login"))

        if verification.code_hash != hash_code(form.code.data):
            flash("Incorrect code. Please try again.", "error")
            return render_template("auth/verify.html", form=form)

        # Correct code: consume it, trust this device, log the admin in
        verification.consumed = True

        device_token = generate_device_token()
        trusted_device = TrustedDevice(
            admin_id=admin_id,
            device_token=device_token,
            user_agent=request.headers.get("User-Agent", "")[:255],
        )
        db.session.add(trusted_device)
        db.session.commit()

        admin = db.session.get(Admin, admin_id)
        login_user(admin)
        session.pop("pending_admin_id", None)

        response = make_response(redirect(url_for("dashboard.index")))
        max_age_days = current_app.config["TRUSTED_DEVICE_MAX_AGE_DAYS"]
        response.set_cookie(
            current_app.config["TRUSTED_DEVICE_COOKIE_NAME"],
            device_token,
            max_age=max_age_days * 24 * 60 * 60,
            httponly=True,
            secure=not current_app.debug,  # allow http on localhost in debug
            samesite="Lax",
        )
        return response

    return render_template("auth/verify.html", form=form)


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.home"))


# ------------------------------------------------------------ manage admins

@auth_bp.route("/admins", methods=["GET", "POST"])
@login_required
def manage_admins():
    """Any logged-in admin can add another — there's no hierarchy/roles,
    every admin has equal access to every committee. This is the
    self-service replacement for the old CLI-only create_admin command."""
    form = AddAdminForm()

    if form.validate_on_submit():
        existing = Admin.query.filter(
            (Admin.username == form.username.data) | (Admin.email == form.email.data)
        ).first()
        if existing:
            flash("An admin with that username or email already exists.", "danger")
        else:
            new_admin = Admin(username=form.username.data.strip(), email=form.email.data.strip())
            new_admin.set_password(form.password.data)
            db.session.add(new_admin)
            db.session.commit()
            flash(f"Admin '{new_admin.username}' added successfully.", "success")
            return redirect(url_for("auth.manage_admins"))

    admins = Admin.query.order_by(Admin.created_at.asc()).all()
    return render_template("admin/index.html", form=form, admins=admins)


@auth_bp.route("/admins/<int:admin_id>/delete", methods=["POST"])
@login_required
def delete_admin(admin_id):
    admin_to_delete = db.session.get(Admin, admin_id)
    if admin_to_delete is None:
        flash("Admin not found.", "danger")
        return redirect(url_for("auth.manage_admins"))

    if Admin.query.count() <= 1:
        flash("Can't remove the last remaining admin — the app would become inaccessible.", "danger")
        return redirect(url_for("auth.manage_admins"))

    was_self = admin_to_delete.id == current_user.id
    db.session.delete(admin_to_delete)
    db.session.commit()
    flash(f"Admin '{admin_to_delete.username}' removed.", "info")

    if was_self:
        logout_user()
        return redirect(url_for("auth.login"))

    return redirect(url_for("auth.manage_admins"))