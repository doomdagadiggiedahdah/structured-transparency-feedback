"""LLM integration for generating reports from participant feedback."""
import os
from typing import Any
from anthropic import Anthropic


def generate_report(feedback: list[dict[str, Any]]) -> str:
    """Generate a report from participant feedback using Claude Haiku 4.5.
    
    Args:
        feedback: List of feedback items, each with 'question', 'answer', 'timestamp'
        
    Returns:
        Generated report text from the LLM
        
    Raises:
        ValueError: If ANTHROPIC_API_KEY is not set
        Exception: If API call fails
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    
    if not feedback:
        return "No feedback collected yet."
    
    # Format feedback for the prompt
    feedback_text = "\n\n".join([
        f"Q: {item['question']}\nA: {item['answer']}\nTimestamp: {item['timestamp']}"
        for item in feedback
    ])
    
    prompt = f"""You are analyzing participant feedback from a transparency session. Below is the collected feedback:

{feedback_text}

Please provide a concise summary and analysis of the feedback, highlighting key themes, insights, and any notable patterns or concerns."""
    
    client = Anthropic(api_key=api_key)
    
    message = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=2048,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return message.content[0].text
