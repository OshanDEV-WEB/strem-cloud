FROM python:3.10-slim

# අවශ්‍ය ටූල්ස් සහ FFmpeg විතරක් ඉන්ස්ටෝල් කරනවා
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# අවශ්‍ය Libraries ටික ඉන්ස්ටෝල් කරනවා
RUN pip install --no-cache-dir streamlink fastapi uvicorn pydantic

COPY main.py .

CMD ["python", "main.py"]
