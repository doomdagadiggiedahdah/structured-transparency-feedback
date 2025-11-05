"""Tests for SessionData model."""
import pytest
from datetime import datetime
from event_server.models import SessionData


def test_session_data_initialization():
    """Test SessionData can be initialized."""
    session = SessionData(session_id="test-123")
    assert session.session_id == "test-123"
    assert session.questions == []
    assert session.is_collecting is True
    assert session.expire_time is None
    assert session.feedback == []
    assert session.generated_report is None


def test_session_data_to_dict():
    """Test SessionData.to_dict() method."""
    session = SessionData(session_id="test-456")
    session.questions = ["Question 1", "Question 2"]
    
    result = session.to_dict()
    assert result["session_id"] == "test-456"
    assert result["questions"] == ["Question 1", "Question 2"]
    assert result["is_collecting"] is True
    assert result["expire_time"] is None
    assert result["generated_report"] is None


def test_add_feedback():
    """Test adding feedback to session."""
    session = SessionData(session_id="test-789")
    session.questions = ["Q1", "Q2"]
    
    session.add_feedback(["Answer 1", "Answer 2"])
    
    assert len(session.feedback) == 2
    assert session.feedback[0]["question"] == "Q1"
    assert session.feedback[0]["answer"] == "Answer 1"
    assert session.feedback[1]["question"] == "Q2"
    assert session.feedback[1]["answer"] == "Answer 2"
    assert "timestamp" in session.feedback[0]


def test_add_feedback_skips_empty():
    """Test that empty answers are skipped."""
    session = SessionData(session_id="test-101")
    session.questions = ["Q1", "Q2", "Q3"]
    
    session.add_feedback(["Answer 1", "", "Answer 3"])
    
    assert len(session.feedback) == 2
    assert session.feedback[0]["answer"] == "Answer 1"
    assert session.feedback[1]["answer"] == "Answer 3"
