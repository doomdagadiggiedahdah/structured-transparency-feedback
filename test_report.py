"""Quick test script to verify report generation works."""
import os
import sys

# Add project to path
sys.path.insert(0, '/home/ubuntu/structured-transparency')

from event_server.models import SessionData
from event_server.llm import generate_report

# Create session with some test feedback
session = SessionData(session_id="test-123")
session.questions = ["What did you think?", "What would you improve?"]

# Add some realistic feedback
session.add_feedback([
    "It was really insightful and I learned a lot about transparency.",
    "Maybe add more time for discussion at the end."
])

session.add_feedback([
    "Great content but audio quality could be better.",
    "Would love more real-world examples."
])

print("=" * 60)
print("TEST: Report Generation")
print("=" * 60)
print(f"\nSession ID: {session.session_id}")
print(f"Questions: {len(session.questions)}")
print(f"Feedback items: {len(session.feedback)}")
print("\nFeedback collected:")
for i, item in enumerate(session.feedback, 1):
    print(f"  {i}. Q: {item['question']}")
    print(f"     A: {item['answer'][:50]}...")

print("\n" + "=" * 60)
print("Generating report with Claude Haiku 4.5...")
print("=" * 60)

try:
    report = generate_report(session.feedback)
    session.generated_report = report
    
    print("\n✅ Report generated successfully!\n")
    print("REPORT:")
    print("-" * 60)
    print(report)
    print("-" * 60)
    
except ValueError as e:
    print(f"\n❌ Error: {e}")
    print("\nMake sure ANTHROPIC_API_KEY is set:")
    print("  export ANTHROPIC_API_KEY='your-key-here'")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ Test passed! Report generation works.")
