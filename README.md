# plate-censor

A CLI tool to detect and censor license plates in images using YOLO object detection.

## Features

- Automatic license plate detection using YOLOv8
- Three censoring methods: gaussian blur, pixelate, or black fill
- Process single images or entire directories
- Recursive directory processing
- Configurable detection confidence and blur strength
- Adjustable padding around detected plates

## Installation

```bash
pip install -e .
```

The YOLO model is automatically downloaded from [HuggingFace](https://huggingface.co/nickmuchi/yolov8n-licence-plate-detection) on first use.

## Usage

```bash
plate-censor INPUT [OPTIONS]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `INPUT` | Image file or directory to process (required) |

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `-o, --output` | auto | Output path (file or directory) |
| `-m, --method` | `gaussian` | Censoring method: `gaussian`, `pixelate`, or `black` |
| `-s, --strength` | `15` | Blur radius or pixel block size |
| `-c, --confidence` | `0.5` | Detection confidence threshold (0.0-1.0) |
| `-p, --padding` | `0.1` | Padding around plates as percentage (0.1 = 10%) |
| `-r, --recursive` | off | Process subdirectories recursively |

### Examples

```bash
# Process a single image with default settings
plate-censor photo.jpg

# Specify output path and use pixelate method
plate-censor photo.jpg -o censored.jpg -m pixelate

# Process directory recursively with lower confidence threshold
plate-censor photos/ -r -c 0.3

# Strong gaussian blur with extra padding
plate-censor photo.jpg -s 30 -p 0.2

# Black out plates completely
plate-censor photo.jpg -m black
```

### Default Output Naming

When `-o` is not specified:
- Single image: `photo.jpg` → `photo_censored.jpg`
- Directory: `photos/` → `photos_censored/`

## Requirements

- Python 3.8+
- ultralytics
- huggingface-hub
- Pillow
- click
- numpy

## License

MIT
