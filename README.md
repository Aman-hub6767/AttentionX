# AttentionX — AI Content Repurposing Engine

Long-form videos ko automatically viral short clips me convert karta hai.

## Setup & Run

### Requirements
- Python 3.8+
- FFmpeg installed (`sudo apt install ffmpeg` ya macOS: `brew install ffmpeg`)

### Installation

```bash
# 1. Clone/download project
cd attentionx

# 2. Virtual environment banao (recommended)
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# 3. Dependencies install karo
pip install -r requirements.txt

# 4. Server start karo
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Browser me open karo
```
http://localhost:8000
```

---

## Features

| Feature | Technology |
|---|---|
| Audio Peak Detection | FFmpeg volumedetect |
| Video Cutting | FFmpeg |
| Vertical 9:16 Crop | FFmpeg scale + crop |
| Caption Overlay | FFmpeg drawtext |
| Hook Generation | Rule-based AI logic |
| File Upload API | FastAPI + python-multipart |
| Frontend | Vanilla HTML/CSS/JS |

## Project Structure

```
attentionx/
├── app.py              # FastAPI backend (main logic)
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # Frontend UI
├── static/             # CSS/JS assets
├── uploads/            # User uploaded videos (auto-created)
└── output/             # Generated clips (auto-created)
```

## How it works

1. **Upload** — User apna long video upload karta hai
2. **Analysis** — FFmpeg audio volume analyze karta hai
3. **Peak Detection** — High-energy moments detect hote hain
4. **Clip Cutting** — Best 3-5 moments cut hote hain (~55 sec each)
5. **Vertical Crop** — 16:9 → 9:16 smart crop (Reels/Shorts ready)
6. **Captions** — Catchy hook + AttentionX branding overlay
7. **Download** — Processed clips download ke liye ready

## Demo Workflow

1. Koi bhi MP4 video upload karo (lecture, podcast, etc.)
2. "Generate Viral Clips" button press karo
3. Processing complete hone ka wait karo
4. Generated clips preview karo aur download karo

