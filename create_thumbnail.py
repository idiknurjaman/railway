import os
import json
import shutil
import random
import subprocess
from flask import Flask, request, jsonify
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# Ambil credentials dari environment variable
gdrive_credentials_json = os.getenv("GDRIVE_CREDENTIALS")
if not gdrive_credentials_json:
    raise ValueError("❌ GDRIVE_CREDENTIALS tidak ditemukan di environment variable!")

# Konversi JSON string ke dictionary
gdrive_credentials_dict = json.loads(gdrive_credentials_json)

# Buat credentials untuk Google Drive API
credentials = Credentials.from_service_account_info(gdrive_credentials_dict)
drive_service = build('drive', 'v3', credentials=credentials)

# Fungsi untuk mendapatkan nama file dari Google Drive
def get_filename_from_url(url):
    try:
        file_id = url.split('/')[-2]
        metadata = drive_service.files().get(fileId=file_id, fields='name').execute()
        filename = metadata.get('name')
        filename_without_ext, _ = os.path.splitext(filename)
        return filename_without_ext
    except Exception as e:
        return None

# Fungsi untuk ekstrak frame dari video
def extract_random_jpeg_frame(video_path, output_path):
    try:
        duration_output = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path],
            capture_output=True, text=True, check=True
        )
        duration = float(duration_output.stdout.strip())
        random_time = random.uniform(1, duration - 1)

        subprocess.run([
            "ffmpeg", "-ss", str(random_time), "-i", video_path,
            "-vf", "scale=-2:480", "-vframes", "1", "-q:v", "2", output_path
        ], check=True)
        return True
    except Exception as e:
        return False

@app.route('/', methods=['POST'])
def process_video():
    data = request.get_json()
    video_url = data.get('videoUrl')

    if not video_url:
        return jsonify({'error': 'Video URL not provided'}), 400

    try:
        filename_without_ext = get_filename_from_url(video_url)
        if not filename_without_ext:
            return jsonify({'error': 'Gagal mendapatkan nama file dari Google Drive'}), 500

        output_filename = filename_without_ext + ".mp4"
        jpeg_filename = filename_without_ext + ".jpg"
        output_folder = "/tmp"  # Gunakan direktori sementara di Railway

        subprocess.run(["yt-dlp", "-f", "b", video_url, "-o", output_filename], check=True)

        if not extract_random_jpeg_frame(output_filename, jpeg_filename):
            return jsonify({'error': 'Gagal mengekstrak frame dari video'}), 500

        os.remove(output_filename)

        output_path = os.path.join(output_folder, jpeg_filename)
        shutil.move(jpeg_filename, output_path)

        results = drive_service.files().list(q=f"name='{jpeg_filename}'", spaces='drive', fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        if items:
            file_id = items[0]['id']
        else:
            return jsonify({'error': 'Thumbnail file not found in Google Drive'}), 500

        thumbnail_url = f"https://drive.google.com/uc?export=view&id={file_id}"

        return jsonify({'filename': jpeg_filename, 'thumbnail': thumbnail_url})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
