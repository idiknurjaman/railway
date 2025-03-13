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
    # Coba list file di Google Drive
    results = drive_service.files().list(pageSize=10, fields="files(id, name)").execute()
    files = results.get("files", [])
    return jsonify(files)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
