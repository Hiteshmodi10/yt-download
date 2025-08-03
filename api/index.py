from flask import Flask, request, jsonify, render_template_string
import yt_dlp
import os
import tempfile
import json
from urllib.parse import urlparse
import threading
import time

app = Flask(__name__)

# For Vercel, we'll use a simple in-memory storage for progress
# Note: This won't persist across function calls in production
download_progress = {}

def progress_hook(d):
    """Hook function to track download progress"""
    if d['status'] == 'downloading':
        filename = d.get('filename', 'unknown')
        percent = d.get('_percent_str', '0%')
        speed = d.get('_speed_str', 'N/A')
        eta = d.get('_eta_str', 'N/A')
        
        download_progress[filename] = {
            'percent': percent,
            'speed': speed,
            'eta': eta,
            'status': 'downloading'
        }
    elif d['status'] == 'finished':
        filename = d.get('filename', 'unknown')
        download_progress[filename] = {
            'percent': '100%',
            'speed': 'Complete',
            'eta': 'Finished',
            'status': 'finished'
        }

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/download', methods=['POST'])
def download_video():
    try:
        data = request.get_json()
        video_url = data.get('url')
        quality = data.get('quality', 'highest')
        
        if not video_url:
            return jsonify({'error': 'No URL provided'}), 400
        
        # Validate URL
        parsed = urlparse(video_url)
        if not (parsed.netloc in ['www.youtube.com', 'youtube.com', 'youtu.be', 'm.youtube.com']):
            return jsonify({'error': 'Please provide a valid YouTube URL'}), 400
        
        # For Vercel deployment, we'll return download URLs instead of downloading files
        # This is because Vercel functions have limited execution time and storage
        
        # Quality format mapping for yt-dlp
        quality_formats = {
            'highest': 'best[ext=mp4]/best',
            '4k': 'best[height>=2160][ext=mp4]/best[height>=2160]',
            '1440p': 'best[height>=1440][height<2160][ext=mp4]/best[height>=1440][height<2160]',
            '1080p': 'best[height>=1080][height<1440][ext=mp4]/best[height>=1080][height<1440]',
            '720p': 'best[height>=720][height<1080][ext=mp4]/best[height>=720][height<1080]',
            'audio': 'bestaudio[ext=m4a]/bestaudio'
        }
        
        ydl_opts = {
            'format': quality_formats.get(quality, quality_formats['highest']),
            'noplaylist': True,
            'extractaudio': quality == 'audio',
            'audioformat': 'mp3' if quality == 'audio' else None,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract video info and get direct download URL
            info = ydl.extract_info(video_url, download=False)
            
            title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            uploader = info.get('uploader', 'Unknown')
            
            # Get the best format URL
            formats = info.get('formats', [])
            if quality == 'audio':
                # Find best audio format
                audio_formats = [f for f in formats if f.get('acodec') != 'none']
                if audio_formats:
                    best_format = max(audio_formats, key=lambda x: x.get('abr', 0) or 0)
                else:
                    best_format = formats[-1] if formats else None
            else:
                # Find best video format
                video_formats = [f for f in formats if f.get('vcodec') != 'none' and f.get('height')]
                if video_formats:
                    if quality == 'highest':
                        best_format = max(video_formats, key=lambda x: x.get('height', 0))
                    elif quality == '4k':
                        format_candidates = [f for f in video_formats if f.get('height', 0) >= 2160]
                        best_format = max(format_candidates, key=lambda x: x.get('height', 0)) if format_candidates else max(video_formats, key=lambda x: x.get('height', 0))
                    elif quality == '1440p':
                        format_candidates = [f for f in video_formats if 1440 <= f.get('height', 0) < 2160]
                        best_format = max(format_candidates, key=lambda x: x.get('height', 0)) if format_candidates else max(video_formats, key=lambda x: x.get('height', 0))
                    elif quality == '1080p':
                        format_candidates = [f for f in video_formats if 1080 <= f.get('height', 0) < 1440]
                        best_format = max(format_candidates, key=lambda x: x.get('height', 0)) if format_candidates else max(video_formats, key=lambda x: x.get('height', 0))
                    elif quality == '720p':
                        format_candidates = [f for f in video_formats if 720 <= f.get('height', 0) < 1080]
                        best_format = max(format_candidates, key=lambda x: x.get('height', 0)) if format_candidates else max(video_formats, key=lambda x: x.get('height', 0))
                    else:
                        best_format = max(video_formats, key=lambda x: x.get('height', 0))
                else:
                    best_format = formats[-1] if formats else None
            
            if not best_format:
                return jsonify({'error': 'No suitable format found'}), 400
            
            download_url = best_format.get('url')
            file_size = best_format.get('filesize') or best_format.get('filesize_approx', 0)
            format_note = best_format.get('format_note', 'Unknown quality')
            
            return jsonify({
                'success': True,
                'title': title,
                'duration': duration,
                'uploader': uploader,
                'quality': quality,
                'format_note': format_note,
                'download_url': download_url,
                'file_size': file_size,
                'message': f'Ready to download: "{title}" in {format_note}'
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/progress/<filename>')
def get_progress(filename):
    """Get download progress for a specific file"""
    progress = download_progress.get(filename, {
        'percent': '0%', 
        'speed': 'N/A', 
        'eta': 'N/A',
        'status': 'unknown'
    })
    return jsonify(progress)

# HTML Template embedded in the Python file for Vercel deployment
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Video Downloader</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            padding: 40px;
            width: 100%;
            max-width: 600px;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
        }

        .header h1 {
            color: #333;
            font-size: 2.5rem;
            margin-bottom: 10px;
        }

        .header p {
            color: #666;
            font-size: 1.1rem;
        }

        .download-form {
            margin-bottom: 30px;
        }

        .input-group {
            display: flex;
            margin-bottom: 20px;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }

        #videoUrl {
            flex: 1;
            padding: 15px 20px;
            border: none;
            font-size: 1rem;
            outline: none;
            background: #f8f9fa;
        }

        #videoUrl:focus {
            background: white;
        }

        #downloadBtn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 1rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        #downloadBtn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
        }

        #downloadBtn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .quality-selector {
            margin-top: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .quality-selector label {
            font-weight: bold;
            color: #333;
            font-size: 1rem;
        }

        #qualitySelect {
            flex: 1;
            padding: 10px 15px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 0.95rem;
            background: white;
            outline: none;
            transition: border-color 0.3s ease;
        }

        #qualitySelect:focus {
            border-color: #667eea;
        }

        .status {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            display: none;
        }

        .status.show {
            display: block;
        }

        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

        .download-result {
            background: #e7f3ff;
            border: 1px solid #b3d7ff;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            display: none;
        }

        .download-result.show {
            display: block;
        }

        .download-result h3 {
            color: #0066cc;
            margin-bottom: 15px;
        }

        .video-info {
            margin-bottom: 15px;
        }

        .video-info p {
            margin-bottom: 5px;
            color: #333;
        }

        .download-link-btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: bold;
            text-decoration: none;
            display: inline-block;
            transition: background 0.3s ease;
        }

        .download-link-btn:hover {
            background: #218838;
            text-decoration: none;
            color: white;
        }

        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .youtube-icon {
            color: #ff0000;
            font-size: 2rem;
            margin-bottom: 10px;
        }

        .quality-info {
            background: #e7f3ff;
            border: 1px solid #b3d7ff;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            text-align: center;
        }

        .quality-info h4 {
            color: #0066cc;
            margin-bottom: 8px;
        }

        .quality-info p {
            color: #333;
            font-size: 0.9rem;
        }

        .vercel-notice {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            text-align: center;
        }

        .vercel-notice h4 {
            color: #856404;
            margin-bottom: 8px;
        }

        .vercel-notice p {
            color: #856404;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="youtube-icon">📺</div>
            <h1>YouTube Downloader</h1>
            <p>Get direct download links for YouTube videos</p>
        </div>

        <div class="vercel-notice">
            <h4>🚀 Deployed on Vercel</h4>
            <p>This app generates direct download links. Click the download button to save videos to your device.</p>
        </div>

        <div class="download-form">
            <div class="input-group">
                <input type="text" id="videoUrl" placeholder="Paste YouTube video URL here..." />
                <button id="downloadBtn" onclick="processVideo()">
                    <span id="btnText">Get Download Link</span>
                    <span id="btnLoading" class="loading" style="display: none;"></span>
                </button>
            </div>
            
            <div class="quality-selector">
                <label for="qualitySelect">Quality:</label>
                <select id="qualitySelect">
                    <option value="highest">🏆 Highest Available</option>
                    <option value="4k">🎯 4K (2160p)</option>
                    <option value="1440p">📺 1440p (2K)</option>
                    <option value="1080p">🎬 1080p (Full HD)</option>
                    <option value="720p">📱 720p (HD)</option>
                    <option value="audio">🎵 Audio Only</option>
                </select>
            </div>
        </div>

        <div id="status" class="status">
            <div id="statusMessage"></div>
        </div>

        <div class="quality-info">
            <h4>🎯 How It Works</h4>
            <p><strong>Step 1:</strong> Paste your YouTube URL and select quality<br>
            <strong>Step 2:</strong> Click "Get Download Link" to process the video<br>
            <strong>Step 3:</strong> Click the download button to save the video</p>
        </div>

        <div id="downloadResult" class="download-result">
            <h3>📥 Ready to Download</h3>
            <div id="videoInfo" class="video-info"></div>
            <a id="downloadLink" class="download-link-btn" href="#" target="_blank">📥 Download Video</a>
        </div>
    </div>

    <script>
        function showStatus(message, type = 'success') {
            const status = document.getElementById('status');
            const statusMessage = document.getElementById('statusMessage');
            
            statusMessage.innerHTML = message;
            status.className = `status show ${type}`;
            
            setTimeout(() => {
                status.classList.remove('show');
            }, 5000);
        }

        function setLoading(loading) {
            const btn = document.getElementById('downloadBtn');
            const btnText = document.getElementById('btnText');
            const btnLoading = document.getElementById('btnLoading');
            
            btn.disabled = loading;
            btnText.style.display = loading ? 'none' : 'inline';
            btnLoading.style.display = loading ? 'inline-block' : 'none';
        }

        function showDownloadResult(data) {
            const result = document.getElementById('downloadResult');
            const videoInfo = document.getElementById('videoInfo');
            const downloadLink = document.getElementById('downloadLink');

            const sizeText = data.file_size ? `${(data.file_size / (1024 * 1024)).toFixed(2)} MB` : 'Unknown size';
            const durationText = data.duration ? `${Math.floor(data.duration / 60)}:${(data.duration % 60).toString().padStart(2, '0')}` : 'Unknown duration';

            videoInfo.innerHTML = `
                <p><strong>Title:</strong> ${data.title}</p>
                <p><strong>Uploader:</strong> ${data.uploader}</p>
                <p><strong>Duration:</strong> ${durationText}</p>
                <p><strong>Quality:</strong> ${data.format_note}</p>
                <p><strong>Size:</strong> ${sizeText}</p>
            `;

            downloadLink.href = data.download_url;
            downloadLink.download = `${data.title}.${data.quality === 'audio' ? 'mp3' : 'mp4'}`;
            
            result.classList.add('show');
        }

        async function processVideo() {
            const url = document.getElementById('videoUrl').value.trim();
            const quality = document.getElementById('qualitySelect').value;
            
            if (!url) {
                showStatus('Please enter a YouTube URL', 'error');
                return;
            }

            setLoading(true);
            document.getElementById('downloadResult').classList.remove('show');

            try {
                const response = await fetch('/api/download', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url: url, quality: quality })
                });

                const data = await response.json();

                if (response.ok) {
                    showStatus(data.message, 'success');
                    showDownloadResult(data);
                } else {
                    showStatus(data.error || 'Processing failed', 'error');
                }
            } catch (error) {
                showStatus('Network error: ' + error.message, 'error');
            } finally {
                setLoading(false);
            }
        }

        // Handle Enter key in input
        document.getElementById('videoUrl').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                processVideo();
            }
        });

        // Auto-focus on URL input
        document.getElementById('videoUrl').focus();
    </script>
</body>
</html>
'''

# For Vercel, we need to handle the app differently
def handler(request):
    return app(request.environ, lambda status, headers: None)

if __name__ == '__main__':
    app.run(debug=True)
