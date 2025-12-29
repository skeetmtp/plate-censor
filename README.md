# License Plate Censor

A web application that automatically detects and censors license plates in MP4 videos using YOLOv8.

## Features

- Drag-and-drop video upload
- Uses YOLOv8 model trained specifically for license plate detection
- Processes videos frame-by-frame with real-time progress tracking
- Download censored videos directly from browser
- Fully local - no cloud services required
- GPU acceleration when available, falls back to CPU
- Modern web UI built with plain HTML/CSS/JavaScript (no frameworks)

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- wget (for model download)

## Setup

```bash
./bin/init.sh
```

This will:
1. Create a virtual environment
2. Install dependencies (FastAPI, uvicorn, ultralytics, opencv-python, torch)
3. Download the license plate detection model (~6MB)

## Usage

```bash
./bin/run.sh
```

Then open http://localhost:8000 in your browser.

1. Drag and drop an MP4 video onto the upload area (or click to browse)
2. Wait for processing to complete with real-time progress updates
3. Click "Download Censored Video" when complete

## Project Structure

```
plate-censor/
├── bin/
│   ├── init.sh              # One-time setup
│   └── run.sh               # Run the web server
├── static/
│   └── index.html           # Web UI
├── models/
│   └── license_plate_detector.pt
├── main.py                  # FastAPI server
├── censor.py                # Video processing logic
└── requirements.txt
```

## How It Works

1. Each frame is processed through a YOLOv8 model trained for license plate detection
2. Detected plates are covered with solid black rectangles (with padding for full coverage)
3. Low confidence threshold (0.25) ensures plates are not missed
4. Original video properties (resolution, FPS, duration) are preserved
