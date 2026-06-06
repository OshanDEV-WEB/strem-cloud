import os
import time
import subprocess
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# UI එකේ ඉඳන් ලින්ක්ස් එද්දී block නොවී ඉන්න CORS දානවා
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StreamData(BaseModel):
    zoom_url: str
    zoom_key: str
    yt_target_url: str
    yt_key: str

# මේක තමයි ලයිව් ස්ට්‍රීම් process දෙක background එකේ run කරන function එක
def run_streaming_engines(data: StreamData):
    print("Initializing Virtual Display...")
    subprocess.Popen("Xvfb :99 -ac -screen 0 1280x720x24", shell=True)
    os.environ["DISPLAY"] = ":99"
    
    print("Launching Browser for Zoom...")
    browser_cmd = f"google-chrome --no-sandbox --use-fake-ui-for-media-stream --disable-gpu --window-size=1280,720 --app={data.zoom_url}"
    subprocess.Popen(browser_cmd, shell=True)
    
    time.sleep(20)
    
    print("Starting Zoom to YouTube stream...")
    zoom_ffmpeg_cmd = (
        f"ffmpeg -f x11grab -video_size 1280x720 -i :99.0 "
        f"-f pulse -i default -c:v libx264 -pix_fmt yuv420p -preset fast "
        f"-c:a aac -f flv {data.zoom_key}"
    )
    subprocess.Popen(zoom_ffmpeg_cmd, shell=True)

    print("Monitoring Target YouTube live...")
    while True:
        cmd_get_url = f"streamlink {data.yt_target_url} best --stream-url"
        process = subprocess.run(cmd_get_url, shell=True, capture_output=True, text=True)
        
        if process.returncode == 0 and "http" in process.stdout:
            stream_url = process.stdout.strip()
            print("Target LIVE found! Restreaming...")
            restream_cmd = f"ffmpeg -i '{stream_url}' -vcodec copy -acodec copy -f flv {data.yt_key}"
            subprocess.run(restream_cmd, shell=True)
        else:
            time.sleep(120)

@app.post("/start")
def start_stream(data: StreamData, background_tasks: BackgroundTasks):
    # UI එකෙන් Start එබුවම Render එක හිර වෙන්නේ නැතුව background එකේ වැඩේ පටන් ගන්නවා
    background_tasks.add_task(run_streaming_engines, data)
    return {"status": "success", "message": "Dual Streaming Started Successfully!"}

@app.get("/")
def read_root():
    return {"status": "running"}

if __name__ == "__main__":
    # PulseAudio සවුන්ඩ් සර්වර් එක Background එකේ ස්ටාර්ට් කරනවා
    subprocess.Popen("pulseaudio -D --exit-idle-time=-1", shell=True)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
