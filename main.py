import subprocess
import ctypes
import os
import tempfile
import shutil
from PIL import Image

try:
    import ffmpeg
    ffmpeg_via_pip = True
except ImportError:
    ffmpeg_via_pip = False

youtube_live_url = "https://www.youtube.com/watch?v=0FBiyFpV__g"

yt_dlp_cmd = None
if shutil.which("yt-dlp"):
    yt_dlp_cmd = ["yt-dlp"]
else:
    try:
        subprocess.run(["python3", "-m", "yt_dlp", "--version"], check=True, stdout=subprocess.DEVNULL)
        yt_dlp_cmd = ["python3", "-m", "yt_dlp"]
    except subprocess.CalledProcessError:
        print("yt-dlp が見つかりませんでした。インストールしてください。")
        exit(1)

yt_dlp_cmd += ['-f', 'best', '-g', youtube_live_url]

try:
    stream_url = subprocess.check_output(yt_dlp_cmd, text=True).strip()
    print(f"取得したストリームURL: {stream_url}")
except subprocess.CalledProcessError:
    print("ストリームURLの取得に失敗しました")
    exit(1)

with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_jpg:
    temp_jpg_path = temp_jpg.name

ffmpeg_cmd = None
if shutil.which("ffmpeg"):
    ffmpeg_cmd = ["ffmpeg"]
elif shutil.which("ffmpeg.exe"):
    ffmpeg_cmd = [shutil.which("ffmpeg.exe")]
elif ffmpeg_via_pip:
    ffmpeg_cmd = [ffmpeg.path.FFMPEG_BINARY]
else:
    print("ffmpeg が見つかりませんでした。インストールしてください。")
    exit(1)

ffmpeg_cmd += [
    '-y',
    '-i', stream_url,
    '-vframes', '1',
    '-vf', 'scale=1920:1080',
    temp_jpg_path
]

result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
print(result.stdout)
print(result.stderr)

if not os.path.exists(temp_jpg_path) or os.path.getsize(temp_jpg_path) == 0:
    print("スクリーンショットの取得に失敗しました")
    exit(1)

with tempfile.NamedTemporaryFile(delete=False, suffix=".bmp") as temp_bmp:
    temp_bmp_path = temp_bmp.name

Image.open(temp_jpg_path).convert("RGB").save(temp_bmp_path)

ctypes.windll.user32.SystemParametersInfoW(20, 0, temp_bmp_path, 0)
print("デスクトップの壁紙を更新しました")

os.remove(temp_jpg_path)
