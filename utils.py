import os
import re
import time
import glob
import subprocess
from rich.console import Console

console = Console()

def create_project_dir(topic_name):
    """프로젝트별 독립 폴더를 생성합니다."""
    date_str = time.strftime("%Y%m%d")
    safe_topic = re.sub(r'[^\w\s-]', '', topic_name[:10]).strip().replace(' ', '_')
    path = os.path.join("downloads", f"{date_str}_{safe_topic}")
    os.makedirs(path, exist_ok=True)
    return os.path.abspath(path)

def compress_audio(file_path):
    """FFmpeg를 사용해 오디오를 32k 모노로 압축합니다."""
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if size_mb <= 24: return os.path.abspath(file_path)

    console.print(f"[yellow]⚠️ 용량 초과({size_mb:.1f}MB)! 압축 시작...[/yellow]")
    out = os.path.join(os.path.dirname(file_path), "final_podcast.mp3")
    cmd = ["ffmpeg", "-i", file_path, "-ac", "1", "-b:a", "32k", "-y", out]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return os.path.abspath(out)

def get_latest_source_file():
    files = glob.glob("downloads/*/source.txt")
    return max(files, key=os.path.getmtime) if files else None

def get_latest_project_dir():
    dirs = glob.glob("downloads/*")
    return max(dirs, key=os.path.getmtime) if dirs else None

def get_latest_audio_file():
    files = [f for ext in ['mp3', 'm4a', 'wav'] for f in glob.glob(f"downloads/*/*.{ext}")]
    return max(files, key=os.path.getmtime) if files else None