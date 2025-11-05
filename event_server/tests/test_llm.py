"""Tests for LLM report generation."""
import pytest
import os
from unittest.mock import patch, MagicMock
from event_server.llm import generate_report
from event_server.tests.test_sample_data import SAMPLE_FEEDBACK


def test_generate_report_no_api_key():
    """Test that generate_report raises error without API key."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
            generate_report(SAMPLE_FEEDBACK)


def test_generate_report_empty_feedback():
    """Test generate_report with empty feedback."""
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
        result = generate_report([])
        assert result == "No feedback collected yet."


@patch('event_server.llm.Anthropic')
def test_generate_report_success(mock_anthropic_class):
    """Test successful report generation."""
    # Mock the Anthropic client
    mock_client = MagicMock()
    mock_anthropic_class.return_value = mock_client
    
    # Mock the API response
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="This is a test report about the feedback.")]
    mock_client.messages.create.return_value = mock_message
    
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
        result = generate_report(SAMPLE_FEEDBACK)
    
    # Verify the result
    assert result == "This is a test report about the feedback."
    
    # Verify Anthropic was called correctly
    mock_anthropic_class.assert_called_once_with(api_key="test-key")
    mock_client.messages.create.assert_called_once()
    
    # Verify the model and parameters
    call_kwargs = mock_client.messages.create.call_args.kwargs
    assert call_kwargs["model"] == "claude-3-5-haiku-20241022"
    assert call_kwargs["max_tokens"] == 2048
    assert len(call_kwargs["messages"]) == 1
    assert call_kwargs["messages"][0]["role"] == "user"
    
    # Verify feedback is in the prompt
    prompt = call_kwargs["messages"][0]["content"]
    assert "What did you think about the session?" in prompt
    assert "insightful and engaging" in prompt


@patch('event_server.llm.Anthropic')
def test_generate_report_formats_feedback_correctly(mock_anthropic_class):
    """Test that feedback is formatted correctly in the prompt."""
    mock_client = MagicMock()
    mock_anthropic_class.return_value = mock_client
    
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="Test report")]
    mock_client.messages.create.return_value = mock_message
    
    test_feedback = [
        {
            "question": "Test Q?",
            "answer": "Test A.",
            "timestamp": "2025-11-05T10:00:00"
        }
    ]
    
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
        generate_report(test_feedback)
    
    prompt = mock_client.messages.create.call_args.kwargs["messages"][0]["content"]
    assert "Q: Test Q?" in prompt
    assert "A: Test A." in prompt
    assert "Timestamp: 2025-11-05T10:00:00" in prompt
