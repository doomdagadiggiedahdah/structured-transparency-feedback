"""API routes for event server."""
import os
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, render_template, request

from event_server.models import SessionData

bp = Blueprint("main", __name__)

# Global session state (in production, use Redis or similar)
session_state = SessionData(session_id=os.urandom(16).hex())


@bp.route("/")
def admin():
    """Admin interface for managing session."""
    return render_template("admin.html")


@bp.route("/participant")
def participant():
    """Participant interface for submitting feedback."""
    return render_template("participant.html")


@bp.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


@bp.route("/api/state")
def get_state():
    """Get current session state."""
    return jsonify(session_state.to_dict())


@bp.route("/api/questions", methods=["POST"])
def update_questions():
    """Update session questions."""
    data = request.get_json()
    if not data or "questions" not in data:
        return jsonify({"error": "Missing questions"}), 400
    
    # Filter out empty strings
    session_state.questions = [q.strip() for q in data["questions"] if q.strip()]
    return jsonify({"success": True})


@bp.route("/api/expire-time", methods=["POST"])
def set_expire_time():
    """Set session expiration time."""
    data = request.get_json()
    if not data or "minutes" not in data:
        return jsonify({"error": "Missing minutes"}), 400
    
    try:
        minutes = int(data["minutes"])
        session_state.expire_time = datetime.now() + timedelta(minutes=minutes)
        return jsonify({"success": True})
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid minutes value"}), 400


@bp.route("/api/close-collection", methods=["POST"])
def close_collection():
    """Stop accepting new feedback."""
    session_state.is_collecting = False
    return jsonify({"success": True})


@bp.route("/api/submit-feedback", methods=["POST"])
def submit_feedback():
    """Submit participant feedback."""
    if not session_state.is_collecting:
        return jsonify({"error": "Collection is closed"}), 403
    
    data = request.get_json()
    if not data or "answers" not in data:
        return jsonify({"error": "Missing answers"}), 400
    
    session_state.add_feedback(data["answers"])
    return jsonify({"success": True})
