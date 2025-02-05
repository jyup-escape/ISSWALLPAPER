import subprocess
import ctypes
import os
import tempfile
from PIL import Image

# YouTube Live のURL
youtube_live_url = "https://www.youtube.com/watch?v=0FBiyFpV__g"

# 最新のストリームURLを取得
yt_dlp_cmd = [
    'yt-dlp',
    '-f', 'best',  # 最高品質の動画
    '-g',  # 直接ストリームURLを取得
    youtube_live_url
]

try:
    stream_url = subprocess.check_output(yt_dlp_cmd, text=True).strip()
    print(f"取得したストリームURL: {stream_url}")
except subprocess.CalledProcessError:
    print("ストリームURLの取得に失敗しました")
    exit(1)

# 一時JPEG保存
with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_jpg:
    temp_jpg_path = temp_jpg.name  

# ffmpeg でスクリーンショット取得
ffmpeg_cmd = [
    'ffmpeg',
    '-y',
    '-i', stream_url,  
    '-vframes', '1',  
    '-vf', 'scale=1920:1080',  
    temp_jpg_path  
]

result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
print(result.stdout)  # ffmpeg の出力を確認
print(result.stderr)

# 画像が正常に取得できたか確認
if not os.path.exists(temp_jpg_path) or os.path.getsize(temp_jpg_path) == 0:
    print("スクリーンショットの取得に失敗しました")
    exit(1)

# JPEG → BMP 変換
with tempfile.NamedTemporaryFile(delete=False, suffix=".bmp") as temp_bmp:
    temp_bmp_path = temp_bmp.name  

Image.open(temp_jpg_path).convert("RGB").save(temp_bmp_path)

# Windowsの壁紙を更新
ctypes.windll.user32.SystemParametersInfoW(20, 0, temp_bmp_path, 0)  
print("デスクトップの壁紙を更新しました")

# 一時JPEG削除
os.remove(temp_jpg_path)
