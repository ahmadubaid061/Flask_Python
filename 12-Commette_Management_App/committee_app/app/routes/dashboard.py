from flask import Blueprint
from flask_login import login_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    # TODO: committee cards + "Create New Committee" button
    return {"status": "stub", "page": "admin dashboard"}


@dashboard_bp.route("/committee/<int:committee_id>/explore")
@login_required
def explore(committee_id):
    # TODO: member list with editable status, add/edit/remove controls,
    # with the start-date lock warning described in DOCUMENTATION.md 5.6
    return {"status": "stub", "page": "explore", "committee_id": committee_id}


@dashboard_bp.route("/committee/new")
@login_required
def new_committee():
    # TODO: create-committee form (name, start date, frequency, amount, count)
    return {"status": "stub", "page": "create committee"}
