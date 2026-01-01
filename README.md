# License Plate Censor

A web application that automatically detects and censors license plates in MP4 videos using YOLOv8.

## Features

- **Drag-and-drop video upload** with file validation
- **YOLOv8 license plate detection** with configurable confidence threshold
- **Real-time progress tracking** via Server-Sent Events
- **Temporal smoothing** to reduce flickering in detections
- **Configurable detection threshold** (0.1 to 0.9) for balancing accuracy vs false positives
- **GPU acceleration** when available, falls back to CPU
- **Modern web UI** built with plain HTML/CSS/JavaScript (no frameworks)
- **Fully local processing** - no cloud services required

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager (recommended)
- wget (for model download)

## Setup

```bash
./bin/init.sh
```

This will:
1. Create a virtual environment with Python 3.12.7
2. Install dependencies (FastAPI, uvicorn, ultralytics, opencv-python, torch)
3. Download the license plate detection model (~6MB)

## Usage

```bash
./bin/run.sh
```

Then open http://localhost:8000 in your browser.

### Step-by-step:
1. **Adjust detection threshold** using the slider (lower = more detections, higher = fewer false positives)
2. **Drag and drop** an MP4 video onto the upload area (or click to browse)
3. **Monitor progress** with real-time updates showing frame-by-frame processing
4. **Download** the censored video when processing completes

## Configuration

### Detection Threshold
- **Range**: 0.1 (more detections) to 0.9 (fewer false positives)
- **Default**: 0.15
- **Adjustable**: Via the slider in the web interface

### Processing Settings
- **Padding**: 5px around detected plates for full coverage
- **Censoring**: Solid black rectangles
- **Temporal smoothing**: Tracks plates across frames to reduce flickering
- **Max track age**: 5 frames (plates persist briefly even if not detected)
- **IoU threshold**: 0.3 for matching detections across frames

## Project Structure

```
plate-censor/
├── bin/
│   ├── init.sh              # One-time setup script
│   └── run.sh               # Run the web server
├── static/
│   └── index.html           # Web UI with drag-and-drop
├── models/
│   └── license_plate_detector.pt  # YOLOv8 weights
├── uploads/
│   └── *.mp4                # Temporary uploaded videos
├── outputs/
│   └── *_censored.mp4       # Processed videos
├── main.py                  # FastAPI server
├── censor.py                # Video processing logic
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## How It Works

### Detection Pipeline
1. **Frame extraction**: Video is processed frame-by-frame
2. **License plate detection**: YOLOv8 model identifies potential plates
3. **Temporal tracking**: PlateTracker smooths detections across frames
4. **Censoring**: Black rectangles cover detected regions with padding
5. **Video reconstruction**: Processed frames are recombined into MP4

### Technical Details
- **Model**: YOLOv8 license plate detector (~6MB)
- **Input**: MP4 videos only
- **Output**: MP4 with `mp4v` codec for cross-platform compatibility
- **Processing**: Preserves original resolution, FPS, and duration
- **Progress**: Real-time updates via Server-Sent Events (SSE)

## API Endpoints

- `GET /` - Web interface
- `POST /upload` - Upload video and start processing
- `GET /progress/{job_id}` - Real-time progress updates (SSE)
- `GET /download/{filename}` - Download processed video

## Model Source

The license plate detection model comes from:
https://github.com/Muhammad-Zeerak-Khan/Automatic-License-Plate-Recognition-using-YOLOv8

## Performance

- **Processing speed**: ~10-30 FPS depending on hardware
- **GPU acceleration**: Automatically used when available
- **Memory usage**: ~1-2GB for typical videos
