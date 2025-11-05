#!/bin/bash
set -e

echo "============================================================"
echo "FULL FLOW TEST: Participant → Server → Report"
echo "============================================================"

# Start the server in background
echo ""
echo "Starting event server on port 5001..."
cd /home/ubuntu/structured-transparency
source .venv/bin/activate
PORT=5001 python -m event_server.app &
SERVER_PID=$!

# Wait for server to start
sleep 2

# Test 1: Set questions
echo ""
echo "1️⃣ Setting questions..."
curl -s -X POST http://localhost:5001/api/questions \
  -H "Content-Type: application/json" \
  -d '{"questions": ["What did you think?", "What would you improve?"]}' | jq .

# Test 2: Submit feedback (simulating what the frontend will do)
echo ""
echo "2️⃣ Submitting feedback (simulating participant)..."
curl -s -X POST http://localhost:5001/api/submit-feedback \
  -H "Content-Type: application/json" \
  -d '{"answers": ["It was amazing and insightful!", "More interactive activities would be great."]}' | jq .

# Test 3: Submit more feedback
echo ""
echo "3️⃣ Submitting more feedback..."
curl -s -X POST http://localhost:5001/api/submit-feedback \
  -H "Content-Type: application/json" \
  -d '{"answers": ["Great session overall", "Better audio quality needed"]}' | jq .

# Test 4: Check state
echo ""
echo "4️⃣ Checking session state..."
curl -s http://localhost:5001/api/state | jq '.feedback | length'
echo " feedback items collected"

# Test 5: Generate report
echo ""
echo "5️⃣ Generating report..."
curl -s -X POST http://localhost:5001/api/generate-report \
  -H "Content-Type: application/json" | jq -r '.report'

# Cleanup
echo ""
echo "============================================================"
echo "✅ Full flow test complete!"
echo "============================================================"
kill $SERVER_PID 2>/dev/null || true
