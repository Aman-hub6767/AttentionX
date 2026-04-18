# AttentionX — AI Content Repurposing Engine

Automatically converts long-form videos into viral short clips.

---

## Setup & Run

### Requirements

- Python 3.8+
- FFmpeg installed (`sudo apt install ffmpeg` or macOS: `brew install ffmpeg`)

### Installation

```bash
# 1. Clone/download project
cd attentionx

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the server
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Open in browser:

```
http://localhost:8000
```

---

## Features

| Feature               | Technology                  |
|-----------------------|-----------------------------|
| Audio Peak Detection  | FFmpeg volumedetect         |
| Video Cutting         | FFmpeg                      |
| Vertical 9:16 Crop    | FFmpeg scale + crop         |
| Caption Overlay       | FFmpeg drawtext             |
| Hook Generation       | Rule-based AI logic         |
| File Upload API       | FastAPI + python-multipart  |
| Frontend              | Vanilla HTML/CSS/JS         |

---

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

---

## How It Works

1. **Upload** — User uploads a long-form video
2. **Analysis** — FFmpeg analyzes audio volume
3. **Peak Detection** — High-energy moments are detected
4. **Clip Cutting** — Best 3–5 moments are extracted (~55 sec each)
5. **Vertical Crop** — 16:9 → 9:16 smart crop (Reels/Shorts ready)
6. **Captions** — Catchy hook + AttentionX branding overlay added
7. **Download** — Processed clips ready to download

---

## Demo Workflow

1. Upload any MP4 video (lecture, podcast, interview, etc.)
2. Press the **"Generate Viral Clips"** button
3. Wait for processing to complete
4. Preview the generated clips and download them

---

## Demo Video

▶️ [Watch Demo on Google Drive](https://drive.google.com/file/d/1PQWDbQXNHYRC2NfbtJq6Gj5KrKtIOwTh/view?usp=sharing)