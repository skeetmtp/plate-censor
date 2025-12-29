"""License plate detection and video censoring module."""

import cv2
from pathlib import Path
from ultralytics import YOLO


MODEL_PATH = Path(__file__).parent / "models" / "license_plate_detector.pt"


def load_model():
    """Load the YOLOv8 license plate detection model.

    Returns:
        YOLO model instance configured for license plate detection.

    Raises:
        FileNotFoundError: If the model file is not found.
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found at {MODEL_PATH}. "
            "Run: mkdir -p models && wget -O models/license_plate_detector.pt "
            '"https://github.com/Muhammad-Zeerak-Khan/Automatic-License-Plate-Recognition-using-YOLOv8/raw/refs/heads/main/license_plate_detector.pt"'
        )
    model = YOLO(str(MODEL_PATH))
    return model


def compute_iou(box1, box2):
    """Compute Intersection over Union between two boxes.

    Args:
        box1, box2: Tuples of (x1, y1, x2, y2) coordinates.

    Returns:
        IoU value between 0 and 1.
    """
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    inter = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = area1 + area2 - inter

    return inter / union if union > 0 else 0


class PlateTracker:
    """Track license plates across frames to reduce flickering."""

    def __init__(self, max_age=5, iou_threshold=0.3, smooth_factor=0.7):
        """Initialize the tracker.

        Args:
            max_age: Frames to persist a track without detection.
            iou_threshold: Minimum IoU to match detection to existing track.
            smooth_factor: EMA weight for previous box (higher = smoother).
        """
        self.tracks = {}  # track_id -> {'box': (x1,y1,x2,y2), 'age': int}
        self.next_id = 0
        self.max_age = max_age
        self.iou_threshold = iou_threshold
        self.smooth_factor = smooth_factor

    def update(self, detections):
        """Update tracks with new detections.

        Args:
            detections: List of (x1, y1, x2, y2) tuples from current frame.

        Returns:
            List of boxes to censor (includes persisted tracks).
        """
        matched_tracks = set()
        matched_detections = set()

        # Match detections to existing tracks using greedy IoU
        for det_idx, det_box in enumerate(detections):
            best_iou = 0
            best_track_id = None

            for track_id, track_data in self.tracks.items():
                if track_id in matched_tracks:
                    continue
                iou = compute_iou(det_box, track_data['box'])
                if iou > best_iou and iou >= self.iou_threshold:
                    best_iou = iou
                    best_track_id = track_id

            if best_track_id is not None:
                # Update existing track with smoothed coordinates
                old_box = self.tracks[best_track_id]['box']
                sf = self.smooth_factor
                smoothed_box = (
                    sf * old_box[0] + (1 - sf) * det_box[0],
                    sf * old_box[1] + (1 - sf) * det_box[1],
                    sf * old_box[2] + (1 - sf) * det_box[2],
                    sf * old_box[3] + (1 - sf) * det_box[3],
                )
                self.tracks[best_track_id]['box'] = smoothed_box
                self.tracks[best_track_id]['age'] = 0
                matched_tracks.add(best_track_id)
                matched_detections.add(det_idx)

        # Create new tracks for unmatched detections
        for det_idx, det_box in enumerate(detections):
            if det_idx not in matched_detections:
                self.tracks[self.next_id] = {'box': det_box, 'age': 0}
                self.next_id += 1

        # Age unmatched tracks and remove expired ones
        expired = []
        for track_id in self.tracks:
            if track_id not in matched_tracks:
                self.tracks[track_id]['age'] += 1
                if self.tracks[track_id]['age'] > self.max_age:
                    expired.append(track_id)

        for track_id in expired:
            del self.tracks[track_id]

        # Return all active track boxes
        return [track_data['box'] for track_data in self.tracks.values()]


def censor_plate(frame, x1, y1, x2, y2, padding=5):
    """Draw a solid black rectangle over the detected plate region.

    Args:
        frame: The video frame (numpy array).
        x1, y1, x2, y2: Bounding box coordinates.
        padding: Extra pixels to add around the detection for full coverage.
    """
    h, w = frame.shape[:2]

    # Add padding and clamp to frame bounds
    x1 = max(0, int(x1) - padding)
    y1 = max(0, int(y1) - padding)
    x2 = min(w, int(x2) + padding)
    y2 = min(h, int(y2) + padding)

    # Draw filled black rectangle
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), -1)


def process_video(input_path, output_path=None, progress_callback=None, conf_threshold=0.15):
    """Process a video file, detecting and censoring all license plates.

    Args:
        input_path: Path to the input MP4 video.
        output_path: Path for the output video. If None, uses <input>_censored.mp4.
        progress_callback: Optional function(current_frame, total_frames) for progress updates.
        conf_threshold: Confidence threshold for YOLO detection (default: 0.15).

    Returns:
        Path to the output video file.

    Raises:
        ValueError: If the input file cannot be opened.
    """
    input_path = Path(input_path)

    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_censored.mp4"
    else:
        output_path = Path(output_path)

    # Open input video
    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {input_path}")

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Create video writer with mp4v codec
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

    if not out.isOpened():
        cap.release()
        raise ValueError(f"Cannot create output video: {output_path}")

    # Load detection model
    model = load_model()

    # Initialize tracker for temporal smoothing
    tracker = PlateTracker(max_age=5, iou_threshold=0.3, smooth_factor=0.7)

    frame_count = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Run license plate detection with configurable confidence threshold
            results = model.predict(
                frame,
                conf=conf_threshold,
                verbose=False
            )

            # Extract detection boxes
            detections = []
            for result in results:
                for box in result.boxes:
                    coords = box.xyxy[0].cpu().numpy()
                    detections.append(tuple(coords))

            # Update tracker and get smoothed boxes
            boxes_to_censor = tracker.update(detections)

            # Censor all tracked plates (including persisted ones)
            for box in boxes_to_censor:
                censor_plate(frame, *box)

            # Write censored frame
            out.write(frame)

            frame_count += 1

            # Report progress
            if progress_callback:
                progress_callback(frame_count, total_frames)

    finally:
        cap.release()
        out.release()

    return output_path
