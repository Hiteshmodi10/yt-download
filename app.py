from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
import tempfile
import threading
from urllib.parse import urlparse

app = Flask(__name__)

# Directory to store downloaded videos temporarily
DOWNLOAD_DIR = tempfile.mkdtemp()

# Global variable to store download progress
download_progress = {}
active_downloads = {}

def progress_hook(d):
    """Hook function to track download progress"""
    filename = d.get('filename', 'unknown')
    
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%')
        speed = d.get('_speed_str', 'N/A')
        eta = d.get('_eta_str', 'N/A')
        downloaded = d.get('_downloaded_bytes_str', 'N/A')
        total = d.get('_total_bytes_str', 'N/A')
        
        download_progress[filename] = {
            'percent': percent,
            'speed': speed,
            'eta': eta,
            'downloaded': downloaded,
            'total': total,
            'status': 'downloading'
        }
    elif d['status'] == 'finished':
        download_progress[filename] = {
            'percent': '100%',
            'speed': 'N/A',
            'eta': 'Complete',
            'downloaded': 'Complete',
            'total': 'Complete',
            'status': 'finished'
        }
    elif d['status'] == 'error':
        download_progress[filename] = {
            'percent': '0%',
            'speed': 'N/A',
            'eta': 'Failed',
            'downloaded': 'Error',
            'total': 'Error',
            'status': 'error'
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    try:
        data = request.get_json()
        video_url = data.get('url')
        quality = data.get('quality', 'highest')  # Default to highest quality
        
        if not video_url:
            return jsonify({'error': 'No URL provided'}), 400
        
        # Validate URL
        parsed = urlparse(video_url)
        if not (parsed.netloc in ['www.youtube.com', 'youtube.com', 'youtu.be', 'm.youtube.com']):
            return jsonify({'error': 'Please provide a valid YouTube URL'}), 400
        
        # Quality format mapping
        quality_formats = {
            'highest': 'bestvideo[height>=2160][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height>=1440][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height>=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/bestvideo+bestaudio/best',
            '4k': 'bestvideo[height>=2160][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height>=2160]+bestaudio/best[height>=2160]/best',
            '1440p': 'bestvideo[height>=1440][height<2160][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height>=1440][height<2160]+bestaudio/best[height>=1440][height<2160]/best',
            '1080p': 'bestvideo[height>=1080][height<1440][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height>=1080][height<1440]+bestaudio/best[height>=1080][height<1440]/best',
            '720p': 'bestvideo[height>=720][height<1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height>=720][height<1080]+bestaudio/best[height>=720][height<1080]/best',
            'audio': 'bestaudio[ext=m4a]/bestaudio/best[acodec=mp3]/best'
        }
        
        # Configure yt-dlp options for selected quality
        ydl_opts = {
            'format': quality_formats.get(quality, quality_formats['highest']),
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            'merge_output_format': 'mp4' if quality != 'audio' else 'm4a',
            'writesubtitles': False,
            'writeautomaticsub': False,
            'ignoreerrors': False,
            'extract_flat': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get video info first
            info = ydl.extract_info(video_url, download=False)
            title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            upload_date = info.get('upload_date', '')
            uploader = info.get('uploader', 'Unknown')
            
            # Create a download ID for tracking
            download_id = f"{title}_{quality}"
            active_downloads[download_id] = {
                'title': title,
                'quality': quality,
                'status': 'preparing'
            }
            
            # Initialize progress tracking
            download_progress[download_id] = {
                'percent': '0%',
                'speed': 'N/A',
                'eta': 'Preparing...',
                'downloaded': '0',
                'total': 'Unknown',
                'status': 'preparing'
            }
            
            # Start download in background thread
            def download_thread():
                try:
                    # Update progress tracking to use download_id
                    def custom_progress_hook(d):
                        if d['status'] == 'downloading':
                            percent = d.get('_percent_str', '0%')
                            speed = d.get('_speed_str', 'N/A')
                            eta = d.get('_eta_str', 'N/A')
                            downloaded = d.get('_downloaded_bytes_str', 'N/A')
                            total = d.get('_total_bytes_str', 'N/A')
                            
                            download_progress[download_id] = {
                                'percent': percent,
                                'speed': speed,
                                'eta': eta,
                                'downloaded': downloaded,
                                'total': total,
                                'status': 'downloading'
                            }
                        elif d['status'] == 'finished':
                            download_progress[download_id] = {
                                'percent': '100%',
                                'speed': 'N/A',
                                'eta': 'Complete',
                                'downloaded': 'Complete',
                                'total': 'Complete',
                                'status': 'finished'
                            }
                        elif d['status'] == 'error':
                            download_progress[download_id] = {
                                'percent': '0%',
                                'speed': 'N/A',
                                'eta': 'Failed',
                                'downloaded': 'Error',
                                'total': 'Error',
                                'status': 'error'
                            }
                    
                    # Update yt-dlp options with custom progress hook
                    ydl_opts['progress_hooks'] = [custom_progress_hook]
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([video_url])
                except Exception as e:
                    print(f"Download error: {e}")
                    download_progress[download_id] = {
                        'percent': '0%',
                        'speed': 'N/A',
                        'eta': 'Failed',
                        'downloaded': 'Error',
                        'total': 'Error',
                        'status': 'error'
                    }
            
            threading.Thread(target=download_thread).start()
            
            return jsonify({
                'success': True,
                'title': title,
                'duration': duration,
                'uploader': uploader,
                'quality': quality,
                'downloadId': download_id,
                'message': f'Download started for "{title}" in {quality} quality'
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/progress/<filename>')
def get_progress(filename):
    """Get download progress for a specific file"""
    progress = download_progress.get(filename, {
        'percent': '0%', 
        'speed': 'N/A', 
        'eta': 'N/A',
        'downloaded': 'N/A',
        'total': 'N/A',
        'status': 'unknown'
    })
    return jsonify(progress)

@app.route('/cancel_download', methods=['POST'])
def cancel_download():
    """Cancel an active download"""
    try:
        data = request.get_json()
        download_id = data.get('downloadId')
        
        if download_id in download_progress:
            download_progress[download_id]['status'] = 'cancelled'
            return jsonify({'success': True, 'message': 'Download cancelled'})
        else:
            return jsonify({'error': 'Download not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/downloads')
def list_downloads():
    """List all downloaded files"""
    try:
        files = []
        for filename in os.listdir(DOWNLOAD_DIR):
            filepath = os.path.join(DOWNLOAD_DIR, filename)
            if os.path.isfile(filepath):
                size = os.path.getsize(filepath)
                files.append({
                    'filename': filename,
                    'size': f"{size / (1024*1024):.2f} MB"
                })
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_file/<filename>')
def download_file(filename):
    """Download a file to user's computer"""
    try:
        filepath = os.path.join(DOWNLOAD_DIR, filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print(f"Download directory: {DOWNLOAD_DIR}")
    app.run(debug=True, host='0.0.0.0', port=5000)
