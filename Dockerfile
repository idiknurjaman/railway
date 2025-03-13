FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y yt-dlp ffmpeg

# Copy requirements.txt first to leverage Docker caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Start the application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
