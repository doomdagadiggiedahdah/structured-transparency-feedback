"""Routes for landing page."""
from flask import Blueprint, render_template

bp = Blueprint("main", __name__)


@bp.route("/")
def landing():
    """Landing page with session creation option."""
    return render_template("index.html")


@bp.route("/create-session", methods=["POST"])
def create_session():
    """Create a new transparency session."""
    # Note: Docker container spawning is implemented in app.py
    # This routes file is kept for reference; actual implementation is in app.py
    return render_template("confirmation.html")
