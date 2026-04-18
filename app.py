import imageio_ffmpeg
import os

# FFmpeg aur FFprobe dono ka path set karo (Windows compatible)
_ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
_ffmpeg_dir = os.path.dirname(_ffmpeg_exe)
os.environ["PATH"] = _ffmpeg_dir + os.pathsep + os.environ["PATH"]
FFMPEG = _ffmpeg_exe
FFPROBE = os.path.join(_ffmpeg_dir, "ffprobe.exe")

import uuid
import subprocess
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil

app = FastAPI(title="AttentionX")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("output")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/output", StaticFiles(directory="output"), name="output")


@app.get("/", response_class=HTMLResponse)
async def index():
    with open("templates/index.html") as f:
        return f.read()


@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    if not file.filename.endswith((".mp4", ".mov", ".avi", ".mkv", ".webm")):
        raise HTTPException(400, "Invalid file format. Use MP4, MOV, AVI, MKV or WebM.")

    job_id = str(uuid.uuid4())[:8]
    video_path = UPLOAD_DIR / f"{job_id}_{file.filename}"

    with open(video_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    file_size = os.path.getsize(video_path)
    duration = get_video_duration(str(video_path))

    return {
        "job_id": job_id,
        "filename": file.filename,
        "size_mb": round(file_size / (1024 * 1024), 2),
        "duration_sec": duration,
        "video_path": str(video_path)
    }


@app.post("/process/{job_id}")
async def process_video(job_id: str, body: dict):
    video_path = body.get("video_path")
    if not video_path or not Path(video_path).exists():
        raise HTTPException(404, "Video not found.")

    duration = get_video_duration(video_path)
    peaks = detect_peaks(video_path, duration)
    clips = []

    for i, peak in enumerate(peaks[:5]):
        clip_id = f"{job_id}_clip{i+1}"
        start = max(0, peak["start"])
        end = min(duration, peak["end"])
        clip_duration = end - start

        if clip_duration < 5:
            continue

        raw_clip    = OUTPUT_DIR / f"{clip_id}_raw.mp4"
        vertical_clip = OUTPUT_DIR / f"{clip_id}_vertical.mp4"
        final_clip  = OUTPUT_DIR / f"{clip_id}_final.mp4"
        thumbnail   = OUTPUT_DIR / f"{clip_id}_thumb.jpg"

        cut_clip(video_path, str(raw_clip), start, end)
        make_vertical(str(raw_clip), str(vertical_clip))

        hook = generate_hook(peak.get("keywords", []), i)
        add_captions(str(vertical_clip), str(final_clip), hook)
        extract_thumbnail(str(final_clip), str(thumbnail))

        if final_clip.exists():
            clips.append({
                "clip_id": clip_id,
                "clip_number": i + 1,
                "start_time": round(start, 1),
                "end_time": round(end, 1),
                "duration": round(end - start, 1),
                "hook": hook,
                "energy_score": peak.get("energy_score", 70),
                "keywords": peak.get("keywords", []),
                "video_url": f"/output/{clip_id}_final.mp4",
                "thumbnail_url": f"/output/{clip_id}_thumb.jpg",
            })

    return {
        "job_id": job_id,
        "total_clips": len(clips),
        "clips": clips
    }


def get_video_duration(path: str) -> float:
    try:
        result = subprocess.run(
            [FFPROBE, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, text=True, timeout=30
        )
        return float(result.stdout.strip())
    except:
        return 60.0


def detect_peaks(video_path: str, duration: float) -> list:
    try:
        result = subprocess.run([
            FFMPEG, "-i", video_path,
            "-af", "volumedetect",
            "-vn", "-sn", "-dn",
            "-f", "null", "NUL"
        ], capture_output=True, text=True, timeout=120)

        output = result.stderr
        mean_volume = -30.0
        max_volume  = -10.0

        for line in output.split('\n'):
            if 'mean_volume' in line:
                try:
                    mean_volume = float(line.split(':')[1].strip().replace(' dB', ''))
                except:
                    pass
            if 'max_volume' in line:
                try:
                    max_volume = float(line.split(':')[1].strip().replace(' dB', ''))
                except:
                    pass
    except:
        mean_volume = -30.0
        max_volume  = -10.0

    peaks = []
    segment_length = 55

    keyword_sets = [
        ["success", "achieve", "mindset", "growth", "powerful"],
        ["mistake", "failure", "lesson", "truth", "reality"],
        ["secret", "hack", "strategy", "never", "always"],
        ["transform", "change", "believe", "possible", "future"],
        ["money", "wealth", "time", "freedom", "invest"],
    ]

    num_clips = min(5, max(2, int(duration // 60)))
    step = duration / (num_clips + 1)

    for i in range(num_clips):
        start = step * (i + 0.5) - segment_length / 2
        start = max(5, start)
        end = start + segment_length
        if end > duration - 2:
            end = duration - 2
            start = max(0, end - segment_length)

        energy = 65 + (i * 7 % 25)
        volume_boost = abs(max_volume - mean_volume)
        if volume_boost > 20:
            energy = min(99, energy + 10)

        peaks.append({
            "start": start,
            "end": end,
            "energy_score": energy,
            "keywords": keyword_sets[i % len(keyword_sets)]
        })

    peaks.sort(key=lambda x: x["energy_score"], reverse=True)
    return peaks


def cut_clip(input_path: str, output_path: str, start: float, end: float):
    subprocess.run([
        FFMPEG, "-y",
        "-ss", str(start),
        "-i", input_path,
        "-t", str(end - start),
        "-c:v", "libx264", "-preset", "fast",
        "-c:a", "aac",
        "-movflags", "+faststart",
        output_path
    ], capture_output=True, timeout=300)


def make_vertical(input_path: str, output_path: str):
    subprocess.run([
        FFMPEG, "-y", "-i", input_path,
        "-vf", (
            "scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920:(iw-1080)/2:(ih-1920)/2"
        ),
        "-c:v", "libx264", "-preset", "fast",
        "-c:a", "aac",
        "-crf", "23",
        output_path
    ], capture_output=True, timeout=300)


def add_captions(input_path: str, output_path: str, hook: str):
    # Windows compatible — fontfile nahi, default font use hoga
    safe_hook = (
        hook
        .replace("\\", "\\\\")
        .replace("'",  "\u2019")   # curly apostrophe — ffmpeg safe
        .replace(":",  "\\:")
        .replace("%",  "\\%")
    )

    vf = (
        f"drawbox=x=0:y=ih-200:w=iw:h=200:color=black@0.75:t=fill,"
        f"drawtext=text='{safe_hook}':"
        f"fontsize=52:fontcolor=white:x=(w-text_w)/2:y=h-160:"
        f"borderw=3:bordercolor=black,"
        f"drawbox=x=0:y=0:w=iw:h=110:color=black@0.65:t=fill,"
        f"drawtext=text='AttentionX':"
        f"fontsize=34:fontcolor=#FFD700:x=20:y=30"
    )

    subprocess.run([
        FFMPEG, "-y", "-i", input_path,
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast",
        "-c:a", "aac",
        output_path
    ], capture_output=True, timeout=300)

    # Fallback — agar caption fail ho to bina caption wala copy karo
    if not Path(output_path).exists():
        shutil.copy(input_path, output_path)


def extract_thumbnail(video_path: str, output_path: str):
    subprocess.run([
        FFMPEG, "-y", "-i", video_path,
        "-ss", "00:00:02",
        "-vframes", "1",
        "-q:v", "2",
        output_path
    ], capture_output=True, timeout=60)


def generate_hook(keywords: list, index: int) -> str:
    hooks = [
        "Ye ek mistake tumhari life change kar sakti hai",
        "Is secret ko jaan liya to success guaranteed hai",
        "Sabse important lesson jo school ne kabhi nahi sikhaya",
        "Ye 60 seconds tumhari soch badal dengi",
        "Wo truth jo log sunna nahi chahte",
        "Ek simple trick jo top 1% log use karte hain",
        "Zindagi ka sabse bada wake-up call",
        "Pehle ye suno fir decision lo",
    ]
    return hooks[index % len(hooks)]


@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(404, "File not found")
    return FileResponse(str(file_path), media_type="video/mp4", filename=filename)
