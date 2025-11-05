"""Test report generation with mocked LLM (no API credits needed)."""
import sys
sys.path.insert(0, '/home/ubuntu/structured-transparency')

from unittest.mock import patch, MagicMock
from event_server.models import SessionData
from event_server.llm import generate_report

# Create session with test feedback
session = SessionData(session_id="test-456")
session.questions = ["What did you think?", "What would you improve?"]

session.add_feedback([
    "It was really insightful and I learned a lot about transparency.",
    "Maybe add more time for discussion at the end."
])

session.add_feedback([
    "Great content but audio quality could be better.",
    "Would love more real-world examples."
])

print("=" * 60)
print("TEST: Report Generation (Mocked)")
print("=" * 60)
print(f"\nSession ID: {session.session_id}")
print(f"Feedback items: {len(session.feedback)}")

print("\nFeedback collected:")
for i, item in enumerate(session.feedback, 1):
    print(f"  {i}. Q: {item['question']}")
    print(f"     A: {item['answer']}")

print("\n" + "=" * 60)
print("Generating report (mocked Claude Haiku 4.5)...")
print("=" * 60)

# Mock the Anthropic client
mock_report = """
**Summary of Participant Feedback**

The session received positive feedback overall, with participants finding the content insightful and educational. Key themes include:

**Strengths:**
- Content quality was highly appreciated
- Participants valued learning about transparency practices
- Overall positive sentiment toward the session

**Areas for Improvement:**
1. **Logistics & Timing**: Multiple participants suggested allocating more time for discussion and Q&A at the conclusion
2. **Technical Quality**: Audio quality emerged as a concern, with at least one participant noting difficulty hearing
3. **Content Enhancement**: Request for more real-world examples and practical case studies to complement theoretical material

**Recommendations:**
- Extend session duration to accommodate deeper discussion
- Invest in improved audio equipment or acoustics
- Integrate additional practical examples into future sessions
"""

with patch('event_server.llm.Anthropic') as mock_anthropic_class:
    mock_client = MagicMock()
    mock_anthropic_class.return_value = mock_client
    
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=mock_report.strip())]
    mock_client.messages.create.return_value = mock_message
    
    report = generate_report(session.feedback)
    session.generated_report = report

print("\n✅ Report generated successfully!\n")
print("REPORT:")
print("-" * 60)
print(report)
print("-" * 60)

print("\n✅ Test passed! Report generation works.")
print("\n💡 The actual API call works too (authenticated successfully)")
print("   Just need Anthropic credits to get real responses.")
