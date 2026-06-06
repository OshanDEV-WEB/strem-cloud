FROM python:3.10-slim

# Install Chrome, FFmpeg, Xvfb, Streamlink, Web Servers and Audio tools
RUN apt-get update && apt-get install -y \
    wget gnupg ffmpeg xvfb pulseaudio xdotool \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && pip install --no-cache-dir streamlink==6.1.0 fastapi uvicorn pydantic \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY main.py .

# Run the Python Web API
CMD ["python", "main.py"]
