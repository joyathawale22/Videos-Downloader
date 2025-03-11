from flask import Flask, request, jsonify, render_template, Response
import yt_dlp
import os
import time
import json

app = Flask(__name__, template_folder="templates")

# Default Download Folder
DEFAULT_DOWNLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads", "GenM_Videos")
if not os.path.exists(DEFAULT_DOWNLOAD_FOLDER):
    os.makedirs(DEFAULT_DOWNLOAD_FOLDER)

# Global variable to store progress
progress_data = {"percentage": 0, "eta": "Calculating...", "speed": 0}

def progress_hook(d):
    """Updates progress dynamically during download"""
    global progress_data

    if d['status'] == 'downloading':
        downloaded_bytes = d.get('downloaded_bytes', 0) or 0
        total_bytes = d.get('total_bytes', 1) or 1  # Avoid division by zero
        speed = d.get('speed', 1) or 1  # Bytes per second
        eta = d.get('eta', "Unknown")

        # Ensure proper calculations even if values are missing
        progress_percent = round((downloaded_bytes / total_bytes) * 100, 2)
        time_remaining = f"{eta} sec" if isinstance(eta, (int, float)) else "Calculating..."

        progress_data = {
            "percentage": progress_percent,
            "eta": time_remaining,
            "speed": round(speed / 1_000_000, 2)  # Convert bytes/sec to Mbps
        }

def generate_progress():
    """Streams live progress updates to the frontend"""
    while True:
        time.sleep(1)  # Refresh every second
        yield f"data: {json.dumps(progress_data)}\n\n"

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/progress')
def progress():
    """Endpoint for real-time download progress"""
    return Response(generate_progress(), mimetype='text/event-stream')

@app.route('/download', methods=['POST'])
def download_video():
    global progress_data
    progress_data = {"percentage": 0, "eta": "Calculating...", "speed": 0}  # Reset progress

    data = request.json
    video_url = data.get("url")
    quality = data.get("quality", "best")
    audio_only = data.get("audio_only", False)
    subtitles = data.get("subtitles", False)

    if not video_url:
        return jsonify({"status": "error", "message": "No video URL provided"}), 400

    options = {
        'outtmpl': os.path.join(DEFAULT_DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'format': 'bestaudio' if audio_only else f"best[height<={quality}]",
        'noplaylist': True,
        'progress_hooks': [progress_hook]
    }

    if subtitles:
        options["writesubtitles"] = True
        options["subtitleslangs"] = ['en']

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([video_url])

        progress_data = {"percentage": 100, "eta": "Download Complete!", "speed": 0}
        return jsonify({"status": "success", "message": "Download Complete!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
