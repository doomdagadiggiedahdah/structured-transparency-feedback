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
    # TODO: Spawn Docker container for new session
    # For now, just show confirmation
    return render_template("confirmation.html")
