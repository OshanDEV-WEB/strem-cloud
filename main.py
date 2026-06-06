import os
import time
import subprocess
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StreamData(BaseModel):
    zoom_rtmp_url: str  # සූම් එකෙන් දෙන Live Stream Server URL එක
    zoom_stream_key: str # සූම් එකෙන් දෙන Stream Key එක
    zoom_target_yt: str  # ඒ සූම් එක ලයිව් යන්න ඕන ඔයාගේ YouTube Stream Key එක
    yt_target_url: str   # කොපි කරන්න ඕන අනෙක් YouTube ලින්ක් එක
    yt_key: str          # ඒක ලයිව් යන්න ඕන ඔයාගේ YouTube Stream Key එක

def run_streaming_engines(data: StreamData):
    # 1. පලමු ප්‍රොසෙස් එක: සූම් මීටින් එකේ ලයිව් එක කෙලින්ම ඔයාගේ යූටියුබ් එකට තල්ලු කරනවා
    print("Starting Process 1: Zoom to YouTube...")
    full_zoom_source = f"{data.zoom_rtmp_url}/{data.zoom_stream_key}"
    zoom_ffmpeg_cmd = f"ffmpeg -i '{full_zoom_source}' -vcodec copy -acodec copy -f flv {data.zoom_target_yt}"
    subprocess.Popen(zoom_ffmpeg_cmd, shell=True)

    # 2. දෙවන ප්‍රොසෙස් එක: අනෙක් යූටියුබ් ලයිව් එක ඔයාගේ යූටියුබ් එකට රීස්ට්‍රීම් කරනවා
    print("Starting Process 2: YouTube to YouTube Restream...")
    while True:
        cmd_get_url = f"streamlink {data.yt_target_url} best --stream-url"
        process = subprocess.run(cmd_get_url, shell=True, capture_output=True, text=True)
        
        if process.returncode == 0 and "http" in process.stdout:
            stream_url = process.stdout.strip()
            print("Target YT LIVE found! Restreaming...")
            restream_cmd = f"ffmpeg -i '{stream_url}' -vcodec copy -acodec copy -f flv {data.yt_key}"
            subprocess.run(restream_cmd, shell=True)
        else:
            time.sleep(120)

@app.post("/start")
def start_stream(data: StreamData, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_streaming_engines, data)
    return {"status": "success", "message": "Dual Streaming Started Successfully!"}

@app.get("/")
def read_root():
    return {"status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
