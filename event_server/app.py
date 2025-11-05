from flask import Flask, send_from_directory, render_template_string, render_template, request, jsonify
from event_server.models import SessionData
from event_server.llm import generate_report
from datetime import datetime, timedelta
import json
import os
import uuid

app = Flask(__name__, template_folder="templates", static_folder="static")

# Session data stored in memory (dies when container stops)
session_data = SessionData(
    session_id=os.environ.get("SESSION_ID", "test-session-" + str(uuid.uuid4())[:8])
)

admin_html = """<!DOCTYPE html>
<html>
<head>
    <title>Admin Panel - Structured Transparency</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h2 {
            margin-bottom: 15px;
            color: #333;
            font-size: 18px;
        }
        h3 {
            margin-top: 15px;
            margin-bottom: 10px;
            color: #555;
            font-size: 14px;
        }
        button {
            background: #0066cc;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        button:hover {
            background: #0052a3;
        }
        button.danger {
            background: #d32f2f;
        }
        button.danger:hover {
            background: #b71c1c;
        }
        input, textarea {
            width: 100%;
            padding: 8px;
            margin-bottom: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: inherit;
            font-size: 14px;
        }
        .question-item {
            background: #f9f9f9;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 4px;
            border-left: 3px solid #0066cc;
        }
        .question-item input {
            margin-bottom: 8px;
        }
        .question-buttons {
            display: flex;
            gap: 5px;
        }
        .question-buttons button {
            flex: 1;
            padding: 6px 10px;
            font-size: 12px;
        }
        .share-link {
            background: #e3f2fd;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 15px;
            word-break: break-all;
            font-size: 12px;
        }
        .qr-code {
            text-align: center;
            margin: 15px 0;
        }
        .qr-code img {
            max-width: 200px;
            border: 1px solid #ddd;
        }
        .status {
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 10px;
            font-size: 14px;
        }
        .status.active {
            background: #c8e6c9;
            color: #2e7d32;
        }
        .status.closed {
            background: #ffccbc;
            color: #d84315;
        }
        .expire-input {
            display: flex;
            gap: 5px;
        }
        .expire-input input {
            flex: 1;
            margin: 0;
        }
        .expire-input button {
            margin: 0;
        }
        .feedback-item {
            background: #f9f9f9;
            padding: 10px;
            margin-bottom: 8px;
            border-radius: 4px;
            font-size: 13px;
            border-left: 3px solid #4caf50;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- LEFT PANEL: Share Link & Questions -->
        <div class="card">
            <h2>Share Link</h2>
            <div id="status" class="status active">Data collection: ACTIVE</div>
            <div class="share-link" id="shareLink">Loading...</div>
            <div class="qr-code">
                <div id="qrCode"></div>
            </div>
            
            <h3>Questions</h3>
            <div id="questionsList"></div>
            <div style="margin-top: 10px;">
                <input type="text" id="newQuestionInput" placeholder="Type new question here..." style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 8px;">
                <button onclick="addQuestion()" style="width: 100%;">+ Add Question</button>
            </div>
            <button onclick="updateQuestions()" style="margin-top: 10px; width: 100%; background: #4caf50;">Update Questions</button>
            
            <h3>Expire Time</h3>
            <div class="expire-input">
                <input type="number" id="expireMinutes" placeholder="Minutes" min="1" value="30">
                <button onclick="setExpireTime()">Set</button>
            </div>
            <p id="expireDisplay" style="font-size: 12px; color: #666; margin-top: 5px;"></p>
            
            <button class="danger" onclick="closeCollection()" style="margin-top: 20px; width: 100%;">Close & Generate Report</button>
        </div>

        <!-- RIGHT PANEL: Feedback -->
        <div class="card">
            <h2>Feedback & Responses</h2>
            <div id="feedbackList" style="max-height: 500px; overflow-y: auto;">
                <p style="color: #999; font-size: 14px;">Responses will appear here...</p>
            </div>
        </div>

        <!-- FULL WIDTH: AI Generated Report -->
        <div class="card" id="reportCard" style="grid-column: 1 / -1; display: none;">
            <h2>📊 AI Generated Report</h2>
            <div id="reportContent" style="
                background: #f9f9f9;
                padding: 20px;
                border-radius: 4px;
                border-left: 4px solid #0066cc;
                white-space: pre-wrap;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                max-height: 600px;
                overflow-y: auto;
            ">
                <p style="color: #999;">Report will appear here after generation...</p>
            </div>
        </div>
    </div>

    <script>
        const SESSION_ID = "{{ session_id }}";
        
        function generateShareLink() {
            const baseUrl = window.location.origin;
            return baseUrl + "/participant?session=" + SESSION_ID;
        }

        function generateQRCode() {
            const shareLink = generateShareLink();
            const qrContainer = document.getElementById("qrCode");
            qrContainer.innerHTML = ""; // Clear previous QR code
            new QRCode(qrContainer, {
                text: shareLink,
                width: 200,
                height: 200
            });
        }

        function loadState() {
            fetch("/api/state")
                .then(r => r.json())
                .then(data => {
                    document.getElementById("shareLink").textContent = generateShareLink();
                    document.getElementById("status").textContent = data.is_collecting ? "Data collection: ACTIVE" : "Data collection: CLOSED";
                    document.getElementById("status").className = data.is_collecting ? "status active" : "status closed";
                    
                    renderQuestions(data.questions);
                    renderFeedback(data.feedback);
                    
                    // Show report if it exists
                    if (data.generated_report) {
                        document.getElementById("reportCard").style.display = "block";
                        document.getElementById("reportContent").innerHTML = marked.parse(data.generated_report);
                    } else {
                        document.getElementById("reportCard").style.display = "none";
                    }
                    
                    if (data.expire_time) {
                        const expireDate = new Date(data.expire_time);
                        const now = new Date();
                        const minutes = Math.round((expireDate - now) / 60000);
                        document.getElementById("expireDisplay").textContent = "Expires in: " + (minutes > 0 ? minutes + " minutes" : "Expired");
                    }
                });
        }

        function renderQuestions(questions) {
            const list = document.getElementById("questionsList");
            
            // Get current values to preserve user input
            const currentInputs = Array.from(document.querySelectorAll("#questionsList input")).map(i => i.value);
            
            // Only update if questions actually changed
            if (JSON.stringify(currentInputs) === JSON.stringify(questions)) {
                return; // No change, skip re-render to preserve focus/selection
            }
            
            if (questions.length === 0) {
                list.innerHTML = "<p style='color: #999; font-size: 13px;'>No questions yet</p>";
                return;
            }
            list.innerHTML = questions.map((q, idx) => `
                <div class="question-item">
                    <input type="text" value="${q}" onchange="updateQuestionAt(${idx}, this.value)">
                    <div class="question-buttons">
                        <button onclick="deleteQuestion(${idx})">Delete</button>
                    </div>
                </div>
            `).join("");
        }

        function renderFeedback(feedback) {
            const list = document.getElementById("feedbackList");
            if (feedback.length === 0) {
                list.innerHTML = "<p style='color: #999; font-size: 14px;'>No responses yet</p>";
                return;
            }
            list.innerHTML = `
                <div class="feedback-item" style="text-align: center; padding: 30px;">
                    <div style="font-size: 48px; font-weight: bold; color: #0066cc; margin-bottom: 10px;">
                        ${feedback.length}
                    </div>
                    <div style="font-size: 18px; color: #666;">
                        ${feedback.length === 1 ? 'response' : 'responses'} received
                    </div>
                </div>
            `;
        }

        function addQuestion() {
            const newQuestionInput = document.getElementById("newQuestionInput");
            const newQuestion = newQuestionInput.value.trim();
            
            if (!newQuestion) {
                alert("Please enter a question");
                return;
            }
            
            const questions = Array.from(document.querySelectorAll("#questionsList input")).map(i => i.value);
            questions.push(newQuestion);
            
            fetch("/api/questions", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({questions})
            }).then(() => {
                newQuestionInput.value = "";  // Clear input after adding
                loadState();
            });
        }

        function deleteQuestion(idx) {
            const questions = Array.from(document.querySelectorAll("#questionsList input")).map(i => i.value);
            questions.splice(idx, 1);
            fetch("/api/questions", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({questions})
            }).then(() => loadState());
        }

        function updateQuestionAt(idx, value) {
            const questions = Array.from(document.querySelectorAll("#questionsList input")).map(i => i.value);
            questions[idx] = value;
            // Don't save yet, just update local state
        }

        function updateQuestions() {
            const questions = Array.from(document.querySelectorAll("#questionsList input")).map(i => i.value).filter(q => q.trim());
            fetch("/api/questions", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({questions})
            }).then(() => {
                alert("Questions updated!");
                loadState();
            });
        }

        function setExpireTime() {
            const minutes = parseInt(document.getElementById("expireMinutes").value);
            if (!minutes || minutes < 1) {
                alert("Please enter a valid number of minutes");
                return;
            }
            fetch("/api/expire-time", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({minutes})
            }).then(() => loadState());
        }

        async function closeCollection() {
            if (!confirm("Close data collection and generate AI report? Participants will no longer be able to submit responses.")) {
                return;
            }
            
            const btn = event.target;
            const originalText = btn.textContent;
            btn.disabled = true;
            btn.textContent = "Closing collection...";
            btn.style.cursor = "wait";
            
            try {
                // Close collection
                await fetch("/api/close-collection", {method: "POST"});
                
                // Update button to show generating
                btn.textContent = "🤖 Generating AI report...";
                
                // Generate report
                const response = await fetch("/api/generate-report", {method: "POST"});
                const data = await response.json();
                
                if (data.success) {
                    btn.textContent = "✓ Report Generated!";
                    btn.style.background = "#4caf50";
                } else {
                    btn.textContent = "Error: " + (data.error || "Unknown");
                    btn.style.background = "#f44336";
                }
                
                loadState();
            } catch (error) {
                btn.textContent = "Error: " + error.message;
                btn.style.background = "#f44336";
                btn.disabled = false;
            }
        }

        // Load state on page load and refresh every 2 seconds
        generateQRCode();
        loadState();
        setInterval(loadState, 2000);
    </script>
</body>
</html>"""

participant_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Feedback Form - Structured Transparency</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            margin-bottom: 20px;
            color: #333;
            font-size: 24px;
        }
        .question-block {
            margin-bottom: 25px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }
        textarea {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: inherit;
            font-size: 14px;
            resize: vertical;
            min-height: 80px;
        }
        button {
            background: #0066cc;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
        }
        button:hover {
            background: #0052a3;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .status {
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 20px;
            text-align: center;
            font-size: 14px;
        }
        .status.closed {
            background: #ffccbc;
            color: #d84315;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Feedback Form</h1>
        <div id="status"></div>
        <form id="feedbackForm">
            <div id="questionsList"></div>
            <button type="submit" id="submitBtn">Submit Responses</button>
        </form>
    </div>

    <script>
        const SESSION_ID = "{{ session_id }}";

        function loadQuestions() {
            fetch("/api/state")
                .then(r => r.json())
                .then(data => {
                    const statusDiv = document.getElementById("status");
                    if (!data.is_collecting) {
                        statusDiv.className = "status closed";
                        statusDiv.textContent = "Data collection has closed. No new responses are being accepted.";
                        document.getElementById("submitBtn").disabled = true;
                        return;
                    }
                    
                    const list = document.getElementById("questionsList");
                    if (data.questions.length === 0) {
                        list.innerHTML = "<p style='color: #999;'>No questions yet. Check back soon.</p>";
                        return;
                    }
                    
                    list.innerHTML = data.questions.map((q, idx) => `
                        <div class="question-block">
                            <label>${q}</label>
                            <textarea name="answer_${idx}" placeholder="Your response..."></textarea>
                        </div>
                    `).join("");
                });
        }

        document.getElementById("feedbackForm").addEventListener("submit", (e) => {
            e.preventDefault();
            const formData = new FormData(document.getElementById("feedbackForm"));
            const answers = Array.from(formData.entries()).map(([_, v]) => v);
            
            fetch("/api/submit-feedback", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({answers})
            }).then(r => r.json()).then(data => {
                if (data.success) {
                    alert("Thank you! Your response has been submitted.");
                    document.getElementById("feedbackForm").reset();
                } else {
                    alert("Error: " + (data.error || "Unknown error"));
                }
            });
        });

        loadQuestions();
        setInterval(loadQuestions, 3000);
    </script>
</body>
</html>
"""

@app.route("/")
def admin():
    return render_template_string(admin_html, session_id=session_data.session_id)

@app.route("/participant")
def participant():
    return render_template("participant.html", session_id=session_data.session_id)

@app.route("/api/state")
def get_state():
    return jsonify(session_data.to_dict())

@app.route("/api/questions", methods=["POST"])
def update_questions():
    data = request.json
    session_data.questions = [q for q in data.get("questions", []) if q.strip()]
    return jsonify({"success": True})

@app.route("/api/expire-time", methods=["POST"])
def set_expire_time():
    data = request.json
    minutes = data.get("minutes", 30)
    session_data.expire_time = datetime.now() + timedelta(minutes=minutes)
    return jsonify({"success": True})

@app.route("/api/close-collection", methods=["POST"])
def close_collection():
    session_data.is_collecting = False
    return jsonify({"success": True})

@app.route("/api/submit-feedback", methods=["POST"])
def submit_feedback():
    if not session_data.is_collecting:
        return jsonify({"success": False, "error": "Data collection is closed"}), 400
    
    data = request.json
    
    # Support two formats:
    # 1. New: {"items": [{"question": "Q", "answer": "A"}, ...]}
    # 2. Old: {"answers": ["A1", "A2", ...]} (uses session_data.questions)
    if "items" in data:
        # New format: direct question+answer pairs
        for item in data["items"]:
            if item.get("answer"):  # Only add if answer is not empty
                session_data.feedback.append({
                    "question": item.get("question", ""),
                    "answer": item["answer"],
                    "timestamp": datetime.now().isoformat(),
                })
    else:
        # Old format: just answers (use existing questions)
        answers = data.get("answers", [])
        session_data.add_feedback(answers)
    
    return jsonify({"success": True})

@app.route("/api/generate-report", methods=["POST"])
def generate_report_endpoint():
    """Generate a report from collected feedback using LLM."""
    try:
        if not session_data.feedback:
            return jsonify({"success": False, "error": "No feedback collected yet"}), 400
        
        # Generate report using LLM
        report = generate_report(session_data.feedback)
        session_data.generated_report = report
        
        return jsonify({
            "success": True,
            "report": report
        })
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to generate report: {str(e)}"}), 500

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
