FROM python:3.10-slim

# සර්වර් එක අප්ඩේට් කරලා අවශ්‍ය tools ටික ඉන්ස්ටෝල් කරනවා
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ffmpeg \
    xvfb \
    pulseaudio \
    xdotool \
    && rm -rf /var/lib/apt/lists/*

# Chrome ඉන්ස්ටෝල් කරන්න වෙනම පියවරක් විදිහට ලියනවා (Error නොවෙන්න)
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Pip අප්ඩේට් කරලා Libraries ටික වෙන වෙනම ඉන්ස්ටෝල් කරනවා
RUN pip install --upgrade pip \
    && pip install --no-cache-dir streamlink==6.1.0 \
    && pip install --no-cache-dir fastapi uvicorn pydantic

COPY main.py .

CMD ["python", "main.py"]
