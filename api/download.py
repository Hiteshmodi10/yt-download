from flask import Flask, request, jsonify
import yt_dlp
from urllib.parse import urlparse

app = Flask(__name__)

def handler(request):
    with app.app_context():
        return download_video()

def download_video():
    try:
        if request.method != 'POST':
            return jsonify({'error': 'Method not allowed'}), 405
            
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        video_url = data.get('url')
        quality = data.get('quality', 'highest')
        
        if not video_url:
            return jsonify({'error': 'No URL provided'}), 400
        
        # Validate URL
        parsed = urlparse(video_url)
        if not (parsed.netloc in ['www.youtube.com', 'youtube.com', 'youtu.be', 'm.youtube.com']):
            return jsonify({'error': 'Please provide a valid YouTube URL'}), 400
        
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
