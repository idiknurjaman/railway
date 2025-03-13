import os
import random
import subprocess
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

def get_filename_from_url(url):
    file_id = url.split('/')[-2]
    drive_service = build('drive', 'v3')
    metadata = drive_service.files().get(fileId=file_id, fields='name').execute()
    filename = metadata.get('name')
    filename_without_ext, _ = os.path.splitext(filename)
    return filename_without_ext

def extract_random_jpeg_frame(video_path, output_path):
    duration_output = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path],
        capture_output=True, text=True
    )
    duration = float(duration_output.stdout.strip())
    random_time = random.uniform(1, duration - 1)

    subprocess.run([
        "ffmpeg", "-ss", str(random_time), "-i", video_path,
        "-vf", "scale=-2:480", "-vframes", "1", "-q:v", "2", output_path
    ])

def create_thumbnail(video_url, output_dir):
    try:
        filename_without_ext = get_filename_from_url(video_url)
        output_filename = filename_without_ext + ".mp4"
        jpeg_filename = filename_without_ext + ".jpg"

        subprocess.run(["yt-dlp", "-f", "b", video_url, "-o", output_filename])

        extract_random_jpeg_frame(output_filename, jpeg_filename)

        os.remove(output_filename)

        output_path = os.path.join(output_dir, jpeg_filename)
        os.rename(jpeg_filename, output_path)

        return output_path

    except Exception as e:
        return str(e)
