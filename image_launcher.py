from flask import Flask, render_template, redirect, url_for, jsonify, request
import subprocess
import os
import csv
import json
import time
from datetime import datetime

app = Flask(__name__)

# Track running processes
processes = {}

def read_csv_safely(filepath, max_retries=3, delay=0.1):
    """Safely read CSV file with retry mechanism"""
    for attempt in range(max_retries):
        try:
            data = []
            with open(filepath, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    data.append(row)
            return data
        except (FileNotFoundError, PermissionError, IOError) as e:
            if attempt < max_retries - 1:
                time.sleep(delay)
                continue
            else:
                print(f"Error reading {filepath}: {e}")
                return []

def get_latest_crowd_data():
    """Get the latest crowd data from CSV"""
    # Assuming 'processed_data/crowd_data.csv' is updated by the model in cam1/main.py
    crowd_data_path = 'processed_data/crowd_data.csv'

    if not os.path.exists(crowd_data_path):
        return {"human_count": 0, "timestamp": "No data", "status": "No data available",
                "social_distance_violations": 0, "restricted_entry": 0, "abnormal_activity": 0}

    try:
        data = read_csv_safely(crowd_data_path)
        if data:
            latest = data[-1]  # Get the last row
            return {
                "human_count": int(latest.get('Human Count', 0)),
                "timestamp": latest.get('Time', 'Unknown'),
                "social_distance_violations": int(latest.get('Social Distance violate', 0)),
                "restricted_entry": int(latest.get('Restricted Entry', 0)),
                "abnormal_activity": int(latest.get('Abnormal Activity', 0)),
                "status": "Active"
            }
    except Exception as e:
        print(f"Error processing crowd data: {e}")

    return {"human_count": 0, "timestamp": "Error", "status": "Error reading data",
            "social_distance_violations": 0, "restricted_entry": 0, "abnormal_activity": 0}

@app.route('/')
def login():
    """Login page based on Screenshot (59).jpg"""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CrowdWatch Pro - Login</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #667eea; /* Background color from screenshot */
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }
        .login-container {
            background: #ffffff;
            border-radius: 15px;
            padding: 40px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            text-align: center;
            width: 350px;
        }
        .logo {
            margin-bottom: 20px;
        }
        .logo h2 {
            font-size: 1.8em;
            color: #333;
            margin-bottom: 5px;
        }
        .logo p {
            font-size: 0.9em;
            color: #666;
        }
        .form-group {
            margin-bottom: 20px;
            text-align: left;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: bold;
        }
        .form-group input {
            width: calc(100% - 20px);
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 1em;
        }
        .login-btn {
            background: #764ba2; /* Button color from screenshot */
            color: white;
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            font-size: 1.1em;
            cursor: pointer;
            width: 100%;
            transition: background 0.3s ease;
        }
        .login-btn:hover {
            background: #663c8a;
        }
        .demo-credentials {
            margin-top: 30px;
            border-top: 1px solid #eee;
            padding-top: 20px;
            text-align: left;
            font-size: 0.9em;
            color: #777;
        }
        .demo-credentials p {
            margin: 5px 0;
        }
        .powered-by {
            margin-top: 30px;
            font-size: 0.8em;
            color: #999;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h2>CrowdWatch Pro</h2>
            <p>Real-time crowd monitoring made simple</p>
        </div>
        <form action="/login_submit" method="post">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" placeholder="admin" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" placeholder="admin123" required>
            </div>
            <button type="submit" class="login-btn">➡️ Login to Dashboard</button>
        </form>
        <div class="demo-credentials">
            <p><strong>Demo Credentials</strong></p>
            <p>Monitor: monitor / monitor123</p>
        </div>
        <div class="powered-by">
            <p>Powered by SecureVision Technologies | 24/7 Support +91-900-CROWD-01</p>
        </div>
    </div>
</body>
</html>'''

@app.route('/login_submit', methods=['POST'])
def login_submit():
    username = request.form['username']
    password = request.form['password']
    # Basic authentication for demo purposes
    if (username == 'admin' and password == 'admin123') or \
       (username == 'operator' and password == 'oper123') or \
       (username == 'monitor' and password == 'monitor123'):
        return redirect(url_for('dashboard'))
    else:
        return "Invalid credentials. Please try again." # In a real app, render login with error

@app.route('/dashboard')
def dashboard():
    """Dashboard page with live monitoring centers based on Screenshot (60).jpg"""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CrowdWatch Pro - Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #394264; /* Background color from screenshot */
            color: white;
            margin: 0;
            padding: 0;
        }
        .header {
            background: #2a314c;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header .logo {
            font-weight: bold;
            font-size: 1.2em;
        }
        .header .user-info {
            font-size: 0.9em;
        }
        .header .user-info a {
            color: white;
            text-decoration: none;
            margin-left: 15px;
        }
        .main-content {
            padding: 30px;
            text-align: center;
        }
        .main-content h1 {
            font-size: 2em;
            margin-bottom: 10px;
        }
        .main-content p {
            font-size: 1em;
            color: #ccc;
            margin-bottom: 30px;
        }
        .location-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            justify-content: center;
            max-width: 1000px;
            margin: 0 auto;
        }
        .location-card {
            background: #4a5375;
            border-radius: 10px;
            overflow: hidden;
            text-align: left;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            transition: transform 0.3s ease;
        }
        .location-card:hover {
            transform: translateY(-5px);
        }
        .location-card img {
            width: 100%;
            height: 180px;
            object-fit: cover;
        }
        .location-card-content {
            padding: 20px;
        }
        .location-card-content h3 {
            margin-top: 0;
            font-size: 1.3em;
            color: #fff;
        }
        .location-card-content p {
            font-size: 0.9em;
            color: #ddd;
            margin-bottom: 15px;
            line-height: 1.5;
        }
        .location-card-details {
            font-size: 0.85em;
            color: #bbb;
            margin-bottom: 20px;
        }
        .start-monitoring-btn {
            background: #8e44ad; /* Button color from screenshot */
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            font-size: 0.9em;
            transition: background 0.3s ease;
        }
        .start-monitoring-btn:hover {
            background: #9b59b6;
        }
        .trust-section {
            margin-top: 50px;
            text-align: center;
            color: #ccc;
        }
        .trust-section h4 {
            font-size: 1em;
            margin-bottom: 20px;
        }
        .trust-logos img {
            height: 30px;
            margin: 0 15px;
            filter: grayscale(100%) brightness(180%);
            opacity: 0.7;
        }
        .footer {
            background: #2a314c;
            padding: 20px;
            margin-top: 50px;
            text-align: center;
            font-size: 0.8em;
            color: #bbb;
        }
        .footer a {
            color: #bbb;
            text-decoration: none;
            margin: 0 10px;
        }
        .footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">CrowdWatch Pro</div>
        <div class="user-info">
            Welcome, Admin <a href="/">Logout</a>
        </div>
    </div>

    <div class="main-content">
        <h1>Live Monitoring Centers</h1>
        <p>Select a location to start real-time crowd monitoring</p>

        
    <div class="location-grid">
            <div class="location-card">
                <img src="/static/images/temple.jpeg" alt="Kapaleshwar Temple">
                <div class="location-card-content">
                    <h3>Kapaleshwar Temple</h3>
                    <p>Sacred temple complex with historical significance and high visitor turnout during festivals.</p>
                    <div class="location-card-details">
                        📍 Nashik, Maharashtra | Max 500 people
                    </div>
                    <a href="/start/cam1" class="start-monitoring-btn">Start Monitoring</a>
                </div>
            </div>

            <div class="location-card">
                <img src="/static/images/ghat.jpeg" alt="Godavari Ghat">
                <div class="location-card-content">
                    <h3>Godavari Ghat</h3>
                    <p>Popular riverside destination for pilgrims and tourists, with constant spiritual atmosphere.</p>
                    <div class="location-card-details">
                        📍 Nashik, Maharashtra | Max 800 people
                    </div>
                    <a href="/start/cam2" class="start-monitoring-btn">Start Monitoring</a>
                </div>
            </div>

            <div class="location-card">
                <img src="/static/images/cave.jpeg" alt="Sita Gufa Cave">
                <div class="location-card-content">
                    <h3>Sita Gufa Cave</h3>
                    <p>Ancient cave with mythological importance, offering peaceful environment for meditation.</p>
                    <div class="location-card-details">
                        📍 Nashik, Maharashtra | Max 200 people
                    </div>
                    <a href="/start/cam3" class="start-monitoring-btn">Start Monitoring</a>
                </div>
            </div>
        </div>

        <div class="trust-section">
            <h4>Trusted by Leading Organizations</h4>
            <div class="trust-logos">
                <img src="https://via.placeholder.com/100x30/CCCCCC/000000?text=SecureVision+Tech" alt="SecureVision Tech">
                <img src="https://via.placeholder.com/100x30/CCCCCC/000000?text=Smart+City+Solutions" alt="Smart City Solutions">
                <img src="https://via.placeholder.com/100x30/CCCCCC/000000?text=Vision+Analytics+Pro" alt="Vision Analytics Pro">
                <img src="https://via.placeholder.com/100x30/CCCCCC/000000?text=AI+Monitoring+Systems" alt="AI Monitoring Systems">
            </div>
        </div>
    </div>

    <div class="footer">
        © 2024 CrowdWatch Pro. All rights reserved | Powered by Advanced AI Technology <br>
        <a href="#">24/7 Support</a> |
        <a href="#">Contact Us</a> |
        <a href="#">Documentation</a> |
        <a href="#">Settings</a> |
        <a href="#">Analytics</a>
    </div>
</body>
</html>'''

@app.route('/api/crowd-data')
def api_crowd_data():
    """API endpoint to get latest crowd data"""
    return jsonify(get_latest_crowd_data())

# Part of image_launcher.py
from flask import Response # Make sure Response is imported

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start/<cam>')
def start(cam):
    if cam not in processes or processes[cam].poll() is not None:
        script_path = os.path.join(cam, 'main.py')
        if os.path.exists(script_path):
            processes[cam] = subprocess.Popen(['python', script_path])
            # Give a small delay for the process to start and potentially create CSV
            time.sleep(2)
        else:
            # If cam directory structure doesn't exist, run main.py with cam as argument
            print(f"Error: Script not found at {script_path}")
            return "Error: Monitoring script not found.", 404

    # Determine display name for the camera
    cam_display_name = cam.replace("cam", "Camera ")

    # Render the monitoring page specific to the selected camera
    # This HTML is for the "Monitoring Kapaleshwar Temple" page from Screenshot (61).jpg
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monitoring {cam_name}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #394264; /* Background color from screenshot */
            color: white;
            margin: 0;
            padding: 0;
        }}
        .header {{
            background: #2a314c;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .header .logo {{
            font-weight: bold;
            font-size: 1.2em;
        }}
        .header .nav-buttons a {{
            background: #8e44ad;
            color: white;
            padding: 8px 15px;
            border-radius: 5px;
            text-decoration: none;
            margin-left: 10px;
            transition: background 0.3s ease;
        }}
        .header .nav-buttons a:hover {{
            background: #9b59b6;
        }}
        .monitoring-container {{
            display: flex;
            padding: 30px;
            gap: 30px;
            flex-wrap: wrap;
        }}
        .left-panel {{
            flex: 2;
            min-width: 500px;
        }}
        .right-panel {{
            flex: 1;
            min-width: 300px;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}
        .video-feed-box {{
            background: #4a5375;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .video-feed-box h3 {{
            margin-top: 0;
            margin-bottom: 15px;
            font-size: 1.2em;
        }}
        .video-placeholder {{
            background: black;
            width: 100%;
            padding-bottom: 56.25%; /* 16:9 Aspect Ratio */
            position: relative;
            border-radius: 5px;
        }}
        .video-placeholder img {{
            position: absolute;
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-radius: 5px;
        }}
        .location-info {{
            background: #4a5375;
            border-radius: 10px;
            padding: 20px;
        }}
        .location-info h3 {{
            margin-top: 0;
            margin-bottom: 15px;
            font-size: 1.2em;
        }}
        .info-item {{
            margin-bottom: 10px;
        }}
        .info-item strong {{
            display: inline-block;
            width: 120px;
        }}
        .real-time-analytics, .statistics-box, .sponsored-section {{
            background: #4a5375;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }}
        .real-time-analytics h3, .statistics-box h3, .sponsored-section h3 {{
            margin-top: 0;
            margin-bottom: 15px;
            font-size: 1.2em;
        }}
        .stat-value {{
            font-size: 3em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .stat-label {{
            font-size: 0.9em;
            color: #ddd;
        }}
        .alert-high {{
            animation: pulse 2s infinite;
            background-color: #f00; /* Red background for alerts */
        }}
        @keyframes pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
            100% {{ transform: scale(1); }}
        }}
        .sponsored-item {{
            background: #5a6385;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            text-align: left;
        }}
        .sponsored-item:last-child {{
            margin-bottom: 0;
        }}
        .sponsored-item h4 {{
            margin-top: 0;
            margin-bottom: 5px;
            color: #fff;
        }}
        .sponsored-item p {{
            font-size: 0.85em;
            color: #ccc;
        }}
        .sponsored-item a {{
            color: #8e44ad;
            text-decoration: none;
            font-size: 0.85em;
        }}
        .sponsored-item a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">Monitoring {cam_display_name}</div>
        <div class="nav-buttons">
            <a href="/dashboard">🏠 Back to Home</a>
            <a href="/stop/{cam}">⏹️ Stop Monitoring</a>
        </div>
    </div>

    
    <div class="monitoring-container">
        <div class="left-panel">
            <!-- This HTML snippet is part of the larger HTML structure returned by the /start/<cam> route -->
            <div class="video-feed-box">
                <h3>Glimpse of Nashik</h3>
                <div class="video-placeholder">
                    <video src="/static/images/nashik.mp4" autoplay loop muted alt="Live Video Feed" width="100%"></video>
                </div>
            </div>

            <div class="location-info">
                <h3>Location Information</h3>
                <div class="info-item"><strong>Location Name:</strong> Kapaleshwar Temple</div>
                <div class="info-item"><strong>Description:</strong> Sacred temple complex with historical significance</div>
                <div class="info-item"><strong>Maximum Capacity:</strong> 500 people</div>
                <div class="info-item"><strong>Location:</strong> Mumbai, Maharashtra</div>
                <div class="info-item"><strong>Camera ID:</strong> CAM1</div>
            </div>
        </div>

        <div class="right-panel">
            <div class="real-time-analytics">
                <h3>Real-Time Analytics</h3>
                <div class="stat-value" id="current-count">0</div>
                <div class="stat-label">Current Count</div>
                <hr style="border-color: #5a6385; margin: 15px 0;">
                <div class="stat-value" id="status-text">Normal</div>
            </div>

            <div class="statistics-box">
                <h3>Statistics</h3>
                <div style="display: flex; justify-content: space-around; margin-bottom: 15px;">
                    <div>
                        <div class="stat-value" id="social-distance-violations">0</div>
                        <div class="stat-label">SD VIOLATION</div>
                    </div>
                    <div>
                        <div class="stat-value" id="restricted-entry">0</div>
                        <div class="stat-label">REX TODAY</div>
                    </div>
                </div>
                <div style="display: flex; justify-content: space-around;">
                    <div>
                        <div class="stat-value" id="accuracy">0%</div>
                        <div class="stat-label">ACCURACY</div>
                    </div>
                    <div>
                        <div class="stat-value" id="alerts">0</div>
                        <div class="stat-label">ALERTS</div>
                    </div>
                </div>
            </div>

            <div class="sponsored-section">
                <h2>Emergency Contact Number</h2>
                        <li align="left">Name: "Police Department", number:"100"</li>
                        <li align="left">Name: "Fire Department", number: "101"</li>
                        <li align="left">Name: "Ambulance", number: "102"</li>
                        <li align="left">Name: "Disaster Management", number: "108"</li>
                        <li align="left">Name: "Emergency Helpline", number: "112"</li>
                        <li align="left">Name: "Poison Control", number: "+1-800-222-1222"</li>
                        <li align="left">Name: "Local Hospital (General)", number: "+91-20-12345678"</li>
                        <br><br>
                <h3>Sponsored</h3>
                <div class="sponsored-item">
                    <h4>SecureVision Pro</h4>
                    <p>Advanced AI security solutions for your business</p>
                    <a href="#">Learn more ></a>
                </div>
                <div class="sponsored-item">
                    <h4>Smart Analytics</h4>
                    <p>Premium insights with our analytics package</p>
                    <a href="#">Get deeper insights ></a>
                </div>
                <div class="sponsored-item">
                    <h4>24/7 Support</h4>
                    <p>Always available to assist you with any queries</p>
                    <p style="font-weight: bold; margin-top: 10px;">Call +91-900-CROWD-01</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        let refreshInterval;

        function updateMonitoringDashboard() {{
            fetch('/api/crowd-data')
                .then(response => response.json())
                .then(data => {{
                    document.getElementById('current-count').textContent = data.human_count;
                    document.getElementById('social-distance-violations').textContent = data.social_distance_violations;
                    document.getElementById('restricted-entry').textContent = data.restricted_entry;
                    // Assuming 'accuracy' and 'alerts' are not directly in crowd_data.csv but can be derived or mocked
                    document.getElementById('accuracy').textContent = '95%'; // Placeholder or derived
                    document.getElementById('alerts').textContent = data.abnormal_activity; // Using abnormal_activity for alerts

                    const statusTextElement = document.getElementById('status-text');
                    if (data.status === 'Active') {{
                        statusTextElement.textContent = 'Normal';
                        statusTextElement.classList.remove('alert-high');
                    }} else if (data.status === 'No data available') {{
                        statusTextElement.textContent = 'No Data';
                        statusTextElement.classList.remove('alert-high');
                    }} else {{
                        statusTextElement.textContent = 'Error';
                        statusTextElement.classList.add('alert-high');
                    }}

                    // Highlight current count if high (example threshold)
                    const currentCountElement = document.getElementById('current-count');
                    if (data.human_count > 50) {{ // Example threshold
                        currentCountElement.classList.add('alert-high');
                    }} else {{
                        currentCountElement.classList.remove('alert-high');
                    }}
                }})
                .catch(error => {{
                    console.error('Error fetching data:', error);
                    document.getElementById('status-text').textContent = 'Connection Error';
                    document.getElementById('status-text').classList.add('alert-high');
                }});
        }}

        // Set up interval to update dashboard every 2 seconds
        refreshInterval = setInterval(updateMonitoringDashboard, 2000); // Update every 2 seconds

        // Initial load
        updateMonitoringDashboard();
    </script>
</body>
</html>'''.format(cam_name=cam_display_name, cam_display_name=cam_display_name, cam=cam)

@app.route('/stop/<cam>')
def stop(cam):
    if cam in processes and processes[cam].poll() is None:
        processes[cam].terminate()
        processes[cam].wait()
        del processes[cam]
    return redirect(url_for('dashboard')) # Redirect back to dashboard after stopping

@app.route('/status')
def status():
    """Get status of all camera processes"""
    status_info = {}
    for cam, process in processes.items():
        if process.poll() is None:
            status_info[cam] = "Running"
        else:
            status_info[cam] = "Stopped"
    return jsonify(status_info)

if __name__ == '__main__':
    # Create a dummy 'processed_data' directory and 'crowd_data.csv' for testing if they don't exist
    # In a real scenario, cam1/main.py would generate this.
    os.makedirs('processed_data', exist_ok=True)
    if not os.path.exists('processed_data/crowd_data.csv'):
        with open('processed_data/crowd_data.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Time', 'Human Count', 'Social Distance violate', 'Restricted Entry', 'Abnormal Activity'])
            writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 5, 0, 0, 0])

    # Ensure 'cam1' directory exists for main.py
    os.makedirs('cam1', exist_ok=True)
    # Create a dummy main.py inside cam1 for testing purposes.
    # In a real scenario, this would be your actual model code.
    if not os.path.exists('cam1/main.py'):
        with open('cam1/main.py', 'w') as f:
            f.write('''
import time
import csv
from datetime import datetime
import random

                    # Part of image_launcher.py
import cv2
import numpy as np # Used for dummy frames

# Global variable for video capture
camera = None

def generate_frames():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0) # Try opening default camera (index 0)

    if not camera.isOpened():
        # ... (dummy frame generation logic) ...
    else:
        while True:
            success, frame = camera.read()
            if not success:
                # ... (camera re-initialization/dummy frame fallback) ...
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')  
                    
def generate_dummy_crowd_data():
    """Generates and appends dummy crowd data to crowd_data.csv"""
    human_count = random.randint(1, 100)
    social_distance_violations = random.randint(0, 10)
    restricted_entry = random.randint(0, 2)
    abnormal_activity = random.randint(0, 1)

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    data = [timestamp, human_count, social_distance_violations, restricted_entry, abnormal_activity]

    filepath = '../processed_data/crowd_data.csv'
    with open(filepath, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)
    print(f"Appended: {data}")

if __name__ == '__main__':
    print("Dummy cam1/main.py started. Generating dummy crowd data...")
    while True:
        generate_dummy_crowd_data()
        time.sleep(2) # Generate data every 2 seconds
''')


    app.run(debug=True, host='0.0.0.0', port=5000)