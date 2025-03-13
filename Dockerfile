FROM python:3.9-slim

WORKDIR /app

# Install yt-dlp and ffmpeg
RUN apt-get update && apt-get install -y yt-dlp ffmpeg
RUN pip install -r requirements.txt
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
