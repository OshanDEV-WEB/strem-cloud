import os
import time
import subprocess

# 1. ඔයාගේ YouTube Stream Key එක මෙතනට දාන්න
YOUR_YOUTUBE_RTMP = "rtmp://a.rtmp.youtube.com/live2/YOUR_STREAM_KEY_HERE"

# 2. ඔයාගේ Zoom Meeting Link එක (Password එකත් එක්කම තියෙන ලින්ක් එක)
ZOOM_MEETING_URL = "https://us02web.zoom.us/j/MEETING_ID?pwd=PASSWORD"

def start_zoom_and_stream():
    print("Starting Virtual Display...")
    # සර්වර් එක ඇතුලේ නොපෙනෙන screen එකක් හදනවා (Resolution: 1280x720)
    subprocess.Popen("Xvfb :99 -ac -screen 0 1280x720x24", shell=True)
    os.environ["DISPLAY"] = ":99"
    
    print("Launching Browser and joining Zoom Meeting...")
    # Browser එකෙන් background එකේ Zoom meeting එකට join වෙනවා
    browser_cmd = f"google-chrome --no-sandbox --use-fake-ui-for-media-stream --disable-gpu --window-size=1280,720 --app={ZOOM_MEETING_URL}"
    subprocess.Popen(browser_cmd, shell=True)
    
    # Zoom එක load වෙලා meeting එකට join වෙනකම් තත්පර 15ක් ඉන්නවා
    time.sleep(15)
    
    print("Starting automated restream to YouTube via FFmpeg...")
    # සර්වර් එක ඇතුලේ පෙනෙන Zoom වීඩියෝ එක සහ සවුන්ඩ් එක අරන් YouTube එකට push කරනවා
    ffmpeg_cmd = (
        f"ffmpeg -f x11grab -video_size 1280x720 -i :99.0 "
        f"-f pulse -i default -c:v libx264 -profile:v baseline -pix_fmt yuv420p "
        f"-c:a aac -f flv {YOUR_YOUTUBE_RTMP}"
    )
    subprocess.run(ffmpeg_cmd, shell=True)

if __name__ == "__main__":
    start_zoom_and_stream()
