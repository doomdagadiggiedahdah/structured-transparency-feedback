from flask import Flask, render_template_string, redirect, request
import docker
import uuid
import logging
import os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get public IP from environment or use default
PUBLIC_IP = os.environ.get('PUBLIC_IP', '18.232.152.144')

landing_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Structured Transparency</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            text-align: center;
            background: white;
            padding: 60px 40px;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 500px;
            width: 100%;
            animation: fadeIn 0.5s ease-in;
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .logo {
            font-size: 64px;
            margin-bottom: 20px;
            animation: float 3s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% {
                transform: translateY(0px);
            }
            50% {
                transform: translateY(-10px);
            }
        }
        
        h1 {
            margin: 0 0 10px 0;
            color: #333;
            font-size: 32px;
            font-weight: 700;
        }
        
        .subtitle {
            color: #666;
            font-size: 16px;
            margin-bottom: 40px;
            line-height: 1.5;
        }
        
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 16px 40px;
            font-size: 18px;
            font-weight: 600;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        .features {
            margin-top: 40px;
            padding-top: 30px;
            border-top: 1px solid #e0e0e0;
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            gap: 20px;
        }
        
        .feature {
            flex: 1;
            min-width: 120px;
        }
        
        .feature-icon {
            font-size: 32px;
            margin-bottom: 8px;
        }
        
        .feature-text {
            font-size: 14px;
            color: #666;
            font-weight: 500;
        }
        
        @media (max-width: 600px) {
            .container {
                padding: 40px 30px;
            }
            
            h1 {
                font-size: 28px;
            }
            
            .logo {
                font-size: 48px;
            }
            
            button {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🎯</div>
        <h1>Structured Transparency</h1>
        <p class="subtitle">Create authentic feedback sessions with secure,<br>private data collection</p>
        <form action="/create-session" method="post">
            <button type="submit">✨ Create New Session</button>
        </form>
        
        <div class="features">
            <div class="feature">
                <div class="feature-icon">🔒</div>
                <div class="feature-text">Secure</div>
            </div>
            <div class="feature">
                <div class="feature-icon">⚡</div>
                <div class="feature-text">Fast</div>
            </div>
            <div class="feature">
                <div class="feature-icon">🎤</div>
                <div class="feature-text">Voice Ready</div>
            </div>
        </div>
    </div>
</body>
</html>
"""

confirmation_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Session Created</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="3;url={{ admin_url }}">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            text-align: center;
            background: white;
            padding: 50px 40px;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 500px;
            width: 100%;
            animation: slideIn 0.5s ease-out;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: scale(0.9);
            }
            to {
                opacity: 1;
                transform: scale(1);
            }
        }
        
        .success-icon {
            font-size: 64px;
            margin-bottom: 20px;
            animation: bounce 1s ease;
        }
        
        @keyframes bounce {
            0%, 100% {
                transform: translateY(0);
            }
            50% {
                transform: translateY(-20px);
            }
        }
        
        h1 {
            margin: 0 0 20px 0;
            color: #333;
            font-size: 28px;
            font-weight: 700;
        }
        
        .session-id {
            background: #f0f4ff;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            border: 2px solid #667eea;
        }
        
        .session-id-label {
            color: #667eea;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }
        
        .session-id-value {
            color: #333;
            font-size: 24px;
            font-weight: 700;
            font-family: 'Courier New', monospace;
        }
        
        p {
            color: #666;
            margin: 20px 0;
            font-size: 16px;
        }
        
        .link {
            display: inline-block;
            margin: 20px 0;
            padding: 14px 32px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .link:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }
        
        .back-link {
            color: #667eea;
            text-decoration: none;
            font-size: 14px;
            margin-top: 20px;
            display: inline-block;
        }
        
        .back-link:hover {
            text-decoration: underline;
        }
        
        .countdown {
            color: #999;
            font-size: 14px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">✅</div>
        <h1>Session Created!</h1>
        
        <div class="session-id">
            <div class="session-id-label">Session ID</div>
            <div class="session-id-value">{{ session_id }}</div>
        </div>
        
        <p class="countdown">Redirecting to admin panel in 3 seconds...</p>
        
        <a href="{{ admin_url }}" class="link">🚀 Go to Admin Panel Now</a>
        
        <p><a href="/" class="back-link">← Back to landing page</a></p>
    </div>
</body>
</html>
"""

error_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Error</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #fc5c7d 0%, #6a82fb 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            text-align: center;
            background: white;
            padding: 50px 40px;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 500px;
            width: 100%;
        }
        
        .error-icon {
            font-size: 64px;
            margin-bottom: 20px;
        }
        
        h1 {
            margin: 0 0 20px 0;
            color: #d32f2f;
            font-size: 28px;
            font-weight: 700;
        }
        
        .error-message {
            background: #ffebee;
            color: #c62828;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #d32f2f;
            text-align: left;
        }
        
        .back-link {
            display: inline-block;
            margin-top: 20px;
            padding: 14px 32px;
            background: #666;
            color: white;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .back-link:hover {
            background: #555;
            transform: translateY(-2px);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="error-icon">❌</div>
        <h1>Error Creating Session</h1>
        <div class="error-message">{{ error_message }}</div>
        <a href="/" class="back-link">← Back to Landing Page</a>
    </div>
</body>
</html>
"""

@app.route("/")
def landing():
    return render_template_string(landing_html)

@app.route("/create-session", methods=["POST"])
def create_session():
    try:
        # Generate unique session ID
        session_id = str(uuid.uuid4())[:8]
        
        # Connect to Docker
        client = docker.from_env()
        
        # Find an available port (starting from 8000)
        used_ports = set()
        for container in client.containers.list():
            for port_bindings in container.attrs['NetworkSettings']['Ports'].values():
                if port_bindings:
                    for binding in port_bindings:
                        used_ports.add(int(binding['HostPort']))
        
        # Find next available port
        port = 8000
        while port in used_ports:
            port += 1
        
        logger.info(f"Creating session {session_id} on port {port}")
        
        # Spawn event server container
        container = client.containers.run(
            "session-server:latest",
            name=f"session-{session_id}",
            ports={'5000/tcp': port},
            volumes={
                '/home/ubuntu/quartz': {'bind': '/home/ubuntu/quartz', 'mode': 'rw'},
                '/home/ubuntu/.ssh': {'bind': '/root/.ssh', 'mode': 'ro'}
            },
            environment={
                'SESSION_ID': session_id,
                'PORT': '5000',
                'ANTHROPIC_API_KEY': os.environ.get('ANTHROPIC_API_KEY', ''),
            },
            detach=True,
            remove=False
        )
        
        logger.info(f"Container {container.id} created for session {session_id}")
        
        # Construct admin URL using public IP
        admin_url = f"https://struct.lol:{port + 1000}/"
        
        return render_template_string(
            confirmation_html,
            session_id=session_id,
            admin_url=admin_url
        )
        
    except docker.errors.ImageNotFound:
        logger.error("session-server:latest image not found")
        return render_template_string(
            error_html,
            error_message="Event server image not found. Please build it first."
        ), 500
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        return render_template_string(
            error_html,
            error_message=f"Failed to create session: {str(e)}"
        ), 500

@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
