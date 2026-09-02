from flask import Blueprint

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login")
def login():
    # TODO: real login form + password check + trusted-device cookie check
    # + email verification flow (see DOCUMENTATION.md section 4).
    return {"status": "stub", "page": "login"}


@auth_bp.route("/verify")
def verify():
    # TODO: 6-digit code entry form
    return {"status": "stub", "page": "verify"}
