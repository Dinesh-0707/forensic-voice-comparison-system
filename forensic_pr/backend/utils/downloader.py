from yt_dlp import YoutubeDL
import os

def download_audio(youtube_url, save_path="static/audio"):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(save_path, '%(id)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'quiet': True
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            audio_file = os.path.join(save_path, f"{info['id']}.wav")
            return audio_file
    except Exception as e:
        print(f"[ERROR] Failed to download: {e}")
        return None
