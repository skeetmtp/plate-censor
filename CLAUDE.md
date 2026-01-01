# CLAUDE.md

## Project Overview

License plate censoring web application using YOLOv8 and OpenCV. Automatically detects and censors license plates in MP4 videos with real-time progress tracking and configurable detection thresholds.

## Tech Stack

- **Python 3.10+**
- **FastAPI** for web server with async processing
- **Plain HTML/CSS/JS** frontend (no frameworks)
- **Ultralytics YOLOv8** for license plate detection
- **OpenCV** for video I/O and frame processing
- **PyTorch** backend (automatic GPU/CPU selection)
- **uv** package manager for dependency management

## Key Files

### Core Files
- `main.py` - FastAPI server with async video processing
- `censor.py` - Detection model loading and video processing logic
- `static/index.html` - Web UI with drag-and-drop upload and real-time progress
- `models/license_plate_detector.pt` - YOLOv8 license plate detection weights

### Configuration
- `requirements.txt` - Python dependencies
- `bin/init.sh` - Setup script (venv + deps + model download)
- `bin/run.sh` - Run script for web server

## Commands

```bash
./bin/init.sh   # Setup: venv + deps + model download
./bin/run.sh    # Run the web server (http://localhost:8000)
```

## Architecture

### Backend (`main.py`)

**FastAPI Server Features:**
- Async request handling with background processing
- In-memory progress tracking store
- Server-Sent Events (SSE) for real-time progress updates

**API Endpoints:**
- `GET /` - Serve web interface
- `POST /upload` - Upload video, validate file type, start processing, return job_id
- `GET /progress/{job_id}` - Server-Sent Events for real-time progress updates
- `GET /download/{filename}` - Download processed video

**Processing Flow:**
1. File validation (MP4 only, threshold range 0.0-1.0)
2. Unique job ID generation
3. File storage in `uploads/` directory
4. Background task creation with `asyncio.create_task()`
5. Progress updates via callback function
6. Result storage in `outputs/` directory

### Processing (`censor.py`)

**Core Functions:**
- `load_model()` - Loads YOLOv8 from `models/license_plate_detector.pt`
- `process_video()` - Frame-by-frame processing with progress callback
- `censor_plate()` - Draws black rectangle over detection with 5px padding
- `compute_iou()` - Intersection over Union calculation for tracking

**PlateTracker Class:**
- Temporal smoothing to reduce flickering
- Tracks plates across frames using IoU matching
- Configurable parameters:
  - `max_age=5` - Frames to persist track without detection
  - `iou_threshold=0.3` - Minimum IoU to match detection to existing track
  - `smooth_factor=0.7` - EMA weight for coordinate smoothing

**Processing Pipeline:**
1. Video capture and property extraction (FPS, resolution)
2. Frame-by-frame processing
3. YOLOv8 detection with configurable confidence threshold
4. Temporal tracking and smoothing
5. Plate censoring with padding
6. Frame writing to output video
7. Progress reporting via callback

### Frontend (`static/index.html`)

**UI Features:**
- Vanilla JavaScript (no frameworks)
- Drag-and-drop file upload with visual feedback
- Configurable detection threshold slider (0.1 to 0.9, default 0.15)
- Real-time progress via EventSource (SSE)
- Responsive gradient UI with smooth animations

**Components:**
- Threshold slider with live value display
- Upload area with drag-over effects
- Progress bar with percentage display
- Status text updates
- Download button (appears on completion)
- Error message display

## Detection Settings

### Configurable Parameters
- **Confidence threshold**: 0.15 (default), range 0.1-0.9
- **Padding**: 5px around detected regions
- **Censoring**: Solid black rectangles (RGB: 0,0,0)
- **Temporal tracking**: Enabled by default

### Algorithm Details
- **Detection**: YOLOv8 license plate detector
- **Tracking**: IoU-based matching with exponential smoothing
- **Persistence**: Plates persist for 5 frames even if not detected
- **Smoothing**: 70% weight to previous position, 30% to current detection

## Technical Details

### Video Processing
- **Input**: MP4 videos only
- **Output**: MP4 with `mp4v` codec
- **Codec**: `cv2.VideoWriter_fourcc(*'mp4v')` for cross-platform compatibility
- **Properties**: Original resolution, FPS, and duration preserved

### Performance
- **Processing speed**: ~10-30 FPS depending on hardware
- **GPU acceleration**: Automatically used when available via PyTorch
- **Memory usage**: ~1-2GB for typical videos
- **Model size**: ~6MB YOLOv8 weights

### Error Handling
- File type validation (MP4 only)
- Threshold range validation (0.0-1.0)
- Video file opening validation
- Progress tracking with error states
- SSE connection error handling

## Notes

- **Model source**: https://github.com/Muhammad-Zeerak-Khan/Automatic-License-Plate-Recognition-using-YOLOv8
- **Video codec**: mp4v for cross-platform compatibility
- **Output naming**: `<input>_censored.mp4` in outputs directory
- **Temporary files**: Uploaded videos stored in `uploads/`, processed videos in `outputs/`

## Documentation

[README.md](README.md) - User-facing documentation with setup and usage instructions

## Development Notes

### Key Design Decisions
1. **No frameworks**: Vanilla JS for minimal dependencies and fast loading
2. **SSE for progress**: Efficient real-time updates without polling
3. **Temporal tracking**: Reduces flickering in detections
4. **Configurable threshold**: Allows users to balance accuracy vs false positives
5. **Background processing**: Non-blocking upload and processing

### Future Enhancements
- Multiple video formats support
- Batch processing
- Custom censoring methods (blur, pixelation)
- Region of interest selection
- Performance metrics and logging
