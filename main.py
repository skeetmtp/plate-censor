"""License Plate Censor - FastAPI web application for censoring license plates in videos."""

import asyncio
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse, StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from censor import process_video

app = FastAPI(title="License Plate Censor")

# Store for progress tracking
progress_store = {}

# Temporary storage for uploaded and processed videos
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page."""
    html_file = Path(__file__).parent / "static" / "index.html"
    if not html_file.exists():
        return HTMLResponse(
            content="<h1>Static files not found</h1><p>Please ensure static/index.html exists.</p>",
            status_code=500
        )
    return FileResponse(html_file)


@app.post("/upload")
async def upload_video(file: UploadFile = File(...), threshold: float = Form(0.15)):
    """Handle video upload and start processing."""

    # Validate file type
    if not file.filename.lower().endswith('.mp4'):
        raise HTTPException(status_code=400, detail="Only MP4 files are supported")

    # Validate threshold
    if not 0.0 <= threshold <= 1.0:
        raise HTTPException(status_code=400, detail="Threshold must be between 0.0 and 1.0")

    # Generate unique ID for this job
    job_id = str(uuid.uuid4())

    # Save uploaded file
    input_path = UPLOAD_DIR / f"{job_id}_{file.filename}"
    with open(input_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Initialize progress
    progress_store[job_id] = {
        "current": 0,
        "total": 0,
        "percent": 0,
        "status": "processing",
        "message": "Starting...",
        "output_path": None
    }

    # Start processing in background
    asyncio.create_task(process_video_task(job_id, input_path, threshold))

    return {"job_id": job_id, "message": "Upload successful, processing started"}


async def process_video_task(job_id: str, input_path: Path, threshold: float = 0.15):
    """Process video in background and update progress."""
    try:
        output_path = OUTPUT_DIR / f"{input_path.stem}_censored.mp4"

        def progress_callback(current, total):
            percent = int((current / total) * 100) if total > 0 else 0
            progress_store[job_id].update({
                "current": current,
                "total": total,
                "percent": percent,
                "message": f"Processing frame {current}/{total} ({percent}%)"
            })

        # Run the video processing (blocking operation)
        await asyncio.to_thread(
            process_video,
            input_path,
            output_path,
            progress_callback,
            threshold
        )

        # Update with completion status
        progress_store[job_id].update({
            "status": "complete",
            "percent": 100,
            "message": "Processing complete!",
            "output_path": str(output_path),
            "output_filename": output_path.name
        })

    except Exception as e:
        progress_store[job_id].update({
            "status": "error",
            "message": f"Error: {str(e)}"
        })


@app.get("/progress/{job_id}")
async def get_progress(job_id: str):
    """Get progress for a specific job via Server-Sent Events."""

    async def event_generator():
        """Generate SSE events for progress updates."""
        while True:
            if job_id not in progress_store:
                yield f"data: {{'error': 'Job not found'}}\n\n"
                break

            progress = progress_store[job_id]

            # Send current progress as JSON
            import json
            yield f"data: {json.dumps(progress)}\n\n"

            # Stop streaming if job is complete or errored
            if progress["status"] in ["complete", "error"]:
                break

            await asyncio.sleep(0.5)  # Update every 500ms

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download the processed video file."""
    file_path = OUTPUT_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        file_path,
        media_type="video/mp4",
        filename=filename
    )


# Mount static files directory
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


def main():
    """Run the FastAPI application."""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    main()
