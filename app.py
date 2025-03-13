from flask import Flask, request, jsonify
import os
from create_thumbnail import create_thumbnail

app = Flask(__name__)

@app.route("/create-thumbnail", methods=["POST"])
def create_thumbnail_route():
    video_url = request.json.get("video_url")
    output_dir = "/tmp"  # Direktori sementara di server

    if not video_url:
        return jsonify({"error": "Video URL tidak ditemukan"}), 400

    thumbnail_path = create_thumbnail(video_url, output_dir)

    if isinstance(thumbnail_path, str):
        return jsonify({"error": thumbnail_path}), 500
    else:
        return jsonify({"message": "Thumbnail berhasil dibuat", "thumbnail_path": thumbnail_path})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
