import os
import time
import subprocess

# --- [SETTINGS 1: ZOOM TO YOUTUBE] ---
# ඔයාගේ Zoom ලින්ක් එක සහ Zoom වීඩියෝ එක ලයිව් යන්න ඕන YouTube Stream Key එක
ZOOM_MEETING_URL = "https://us02web.zoom.us/j/MEETING_ID?pwd=PASSWORD"
YT_STREAM_KEY_FOR_ZOOM = "rtmp://a.rtmp.youtube.com/live2/YOUR_STREAM_KEY_1"

# --- [SETTINGS 2: YOUTUBE TO YOUTUBE (RESTREAM)] ---
# ඔයාට කොපි කරලා ලයිව් දාන්න ඕන අනෙක් YouTube චැනල් එකේ Live URL එක සහ ඒක යන්න ඕන Stream Key එක
TARGET_YT_LIVE_URL = "https://www.youtube.com/@TargetChannelName/live"
YT_STREAM_KEY_FOR_RESTREAM = "rtmp://a.rtmp.youtube.com/live2/YOUR_STREAM_KEY_2"

def start_zoom_and_dual_stream():
    # 1. සර්වර් එක ඇතුලේ Zoom එක display කරන්න virtual screen එකක් හදනවා
    print("Starting Virtual Display for Zoom...")
    subprocess.Popen("Xvfb :99 -ac -screen 0 1280x720x24", shell=True)
    os.environ["DISPLAY"] = ":99"
    
    # 2. Browser එකෙන් background එකේ Zoom meeting එකට join වෙනවා
    print("Launching Browser and joining Zoom Meeting...")
    browser_cmd = f"google-chrome --no-sandbox --use-fake-ui-for-media-stream --disable-gpu --window-size=1280,720 --app={ZOOM_MEETING_URL}"
    subprocess.Popen(browser_cmd, shell=True)
    
    # Zoom එක load වෙනකම් තත්පර 20ක් ඉන්නවා
    time.sleep(20)
    
    # 3. පළමු FFmpeg එක: Zoom screen එක capture කරලා පළමු YouTube stream එකට දානවා
    print("Process 1: Streaming Zoom to YouTube Started...")
    zoom_ffmpeg_cmd = (
        f"ffmpeg -f x11grab -video_size 1280x720 -i :99.0 "
        f"-f pulse -i default -c:v libx264 -pix_fmt yuv420p -preset fast "
        f"-c:a aac -f flv {YT_STREAM_KEY_FOR_ZOOM}"
    )
    subprocess.Popen(zoom_ffmpeg_cmd, shell=True)

    # 4. දෙවන FFmpeg එක: අනෙක් YouTube ලයිව් එක auto-check කරලා දෙවන YouTube stream එකට restream කරනවා
    print("Process 2: Checking and Restreaming Target YouTube Live...")
    while True:
        # Streamlink හරහා target live stream එක තියෙනවද බලනවා
        cmd_get_url = f"streamlink {TARGET_YT_LIVE_URL} best --stream-url"
        process = subprocess.run(cmd_get_url, shell=True, capture_output=True, text=True)
        
        if process.returncode == 0 and "http" in process.stdout:
            stream_url = process.stdout.strip()
            print("Target YT Live is active! Starting restream...")
            
            # Target stream එක download කරලා කෙලින්ම ඔයාගේ දෙවැනි stream key එකට push කරනවා
            restream_cmd = f"ffmpeg -i '{stream_url}' -vcodec copy -acodec copy -f flv {YT_STREAM_KEY_FOR_RESTREAM}"
            subprocess.run(restream_cmd, shell=True)
        else:
            print("Target YT Live is offline. Re-checking in 2 minutes...")
            time.sleep(120)

if __name__ == "__main__":
    start_zoom_and_dual_stream()
