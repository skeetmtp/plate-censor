#!/bin/bash
set -e

cd "$(dirname "$0")/.."

echo "=== License Plate Censor - Setup ==="

# Create virtual environment and install dependencies
echo "Installing dependencies..."
uv venv --python 3.12.7
source .venv/bin/activate
uv pip install -r requirements.txt

# Download model
mkdir -p models
if [ ! -f "models/license_plate_detector.pt" ]; then
    echo "Downloading license plate detection model..."
    wget -O models/license_plate_detector.pt \
        "https://github.com/Muhammad-Zeerak-Khan/Automatic-License-Plate-Recognition-using-YOLOv8/raw/refs/heads/main/license_plate_detector.pt"
else
    echo "Model already downloaded"
fi

echo ""
echo "=== Setup complete ==="
echo "Run the app with: ./bin/run.sh"

## Installation

