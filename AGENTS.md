# Repository Guidelines

## Project Structure & Module Organization
- `main.py` hosts the FastAPI server, routes, and background job orchestration.
- `censor.py` contains the YOLOv8 loading, tracking, and video processing pipeline.
- `static/index.html` is the vanilla HTML/CSS/JS UI.
- `models/` stores `license_plate_detector.pt` (downloaded by setup).
- `uploads/` holds temporary user uploads; `outputs/` holds processed videos.
- `bin/` contains setup/run scripts; `requirements.txt` lists Python deps.

## Build, Test, and Development Commands
- `./bin/init.sh` creates a `.venv`, installs dependencies with `uv`, and downloads the model.
- `./bin/run.sh` activates the venv and starts the server (`http://localhost:8000`).
- `uv run main.py` is the direct dev entrypoint if the venv is already active.
- There are no automated tests yet; validate changes manually via the UI.

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indentation and snake_case for functions/variables.
- Keep modules focused: server logic in `main.py`, video logic in `censor.py`.
- Prefer explicit names for processing steps (e.g., `process_video`, `censor_plate`).
- Frontend JS stays in `static/index.html`; avoid introducing frameworks.

## Testing Guidelines
- Manual checks: upload an MP4, watch progress updates, and download the result.
- Confirm output naming uses `<input>_censored.mp4` in `outputs/`.
- If you add tests, keep them lightweight and document how to run them.

## Commit & Pull Request Guidelines
- Git history is minimal; no formal convention yet. Use short, imperative summaries.
- Include a clear description of behavior changes and how you verified them.
- Link relevant issues or include UI screenshots if the frontend changes.

## Security & Configuration Notes
- The app processes local files only; avoid logging raw video data.
- Keep model artifacts out of commits; `models/` is populated by `bin/init.sh`.
- Update `requirements.txt` when adding dependencies.

## Agent-Specific Instructions
- Consult `CLAUDE.md` for architecture and processing details before large changes.
