# CLAUDE.md

## Project Overview

License plate censoring web application using YOLOv8 and OpenCV.

## Tech Stack

- Python 3.10+
- FastAPI for web server
- Plain HTML/CSS/JS frontend (no frameworks)
- Ultralytics YOLOv8 for detection
- OpenCV for video I/O
- PyTorch backend (CPU/GPU)

## Key Files

- `main.py` - FastAPI server with async video processing
- `censor.py` - Detection model loading and video processing
- `static/index.html` - Web UI with drag-and-drop upload
- `models/license_plate_detector.pt` - YOLOv8 weights

## Commands

```bash
./bin/init.sh   # Setup: venv + deps + model download
./bin/run.sh    # Run the web server (http://localhost:8000)
```

## Architecture

### Backend (`main.py`)
- FastAPI server with async request handling
- POST `/upload` - Upload video, returns job_id
- GET `/progress/{job_id}` - Server-Sent Events for real-time progress
- GET `/download/{filename}` - Download processed video
- Background processing using `asyncio.create_task()`
- Progress tracking via in-memory store

### Processing (`censor.py`)
- `load_model()` - Loads YOLOv8 from `models/license_plate_detector.pt`
- `process_video()` - Frame-by-frame processing with progress callback
- `censor_plate()` - Draws black rectangle over detection with 5px padding

### Frontend (`static/index.html`)
- Vanilla JavaScript (no frameworks)
- Drag-and-drop file upload
- Real-time progress via EventSource (SSE)
- Responsive gradient UI

## Detection Settings

- Confidence threshold: 0.25 (low to prefer false positives)
- Padding: 5px around detected regions
- Censoring: Solid black rectangles

## Notes

- Model source: https://github.com/Muhammad-Zeerak-Khan/Automatic-License-Plate-Recognition-using-YOLOv8
- Video codec: mp4v for cross-platform compatibility
- Output naming: `<input>_censored.mp4` in same directory

## Documentation

[README.md](README.md)
