import os
import random
import subprocess

def create_thumbnail(video_url, output_dir):
    try:
        # Unduh video dari URL
        filename_without_ext = "video"
        output_filename = os.path.join(output_dir, filename_without_ext + ".mp4")
        jpeg_filename = os.path.join(output_dir, filename_without_ext + ".jpg")

        subprocess.run(["yt-dlp", "-f", "b", video_url, "-o", output_filename], check=True)

        # Cek durasi video
        duration_output = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", output_filename],
            capture_output=True, text=True, check=True
        )
        duration = float(duration_output.stdout.strip())
        random_time = random.uniform(1, duration - 1)

        # Ekstrak thumbnail
        subprocess.run([
            "ffmpeg", "-ss", str(random_time), "-i", output_filename,
            "-vf", "scale=-2:480", "-vframes", "1", "-q:v", "2", jpeg_filename
        ], check=True)

        os.remove(output_filename)  # Hapus video setelah thumbnail dibuat
        return jpeg_filename

    except Exception as e:
        return str(e)  # Jika error, kembalikan pesan error sebagai string
