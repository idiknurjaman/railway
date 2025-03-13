import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from flask import Flask, request, jsonify

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

@app.route("/test-drive", methods=["GET"])
def test_drive():
    try:
        # Contoh: Dapatkan daftar file di Google Drive
        results = drive_service.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            return jsonify({"message": "Tidak ada file ditemukan di Google Drive."})
        else:
            file_names = [item['name'] for item in items]
            return jsonify({"message": "Koneksi ke Google Drive API berhasil.", "files": file_names})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
