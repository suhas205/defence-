from ultralytics import YOLO
import cv2
import os
from mail import send_alert_image

import sys
MODEL_PATHS = {
    "Normal": r"C:\Users\suhas_t9klwz0\Downloads\best (1).pt",
    "SAR": r"C:\SUHAS_P\defence pro\ship.pt"
}

if len(sys.argv) > 1:
    arg = sys.argv[1]
    if arg in MODEL_PATHS:
        model_path = MODEL_PATHS[arg]
    else:
        model_path = arg
else:
    model_path = MODEL_PATHS["Normal"]

# Load the YOLO model
model = YOLO(model_path)

# Read video source dynamically from a configuration file
try:
    with open("config/live_video_src.txt", "r") as file:
        video_source = file.read().strip()
        if not video_source:
            raise ValueError("Video source is empty. Please provide a valid source in the file.")
except FileNotFoundError:
    raise FileNotFoundError("The configuration file 'config/live_video_src.txt' was not found.")
except Exception as e:
    raise Exception(f"Error reading video source: {e}")

# Check if the video source is a webcam or a video file
if video_source.isdigit():
    video_source = int(video_source)  # Convert webcam index to integer for OpenCV

os.makedirs('results', exist_ok=True)

# Open video source
cap = cv2.VideoCapture(video_source)
if not cap.isOpened():
    raise Exception(f"Error: Unable to open video source '{video_source}'. Check the file path or webcam connection.")

alert_sent = False

print("Press 'q' to quit.")
while True:
    ret, frame = cap.read()
    if not ret:
        print("End of video or unable to read frame.")
        break

    results = model.predict(source=frame, show=False)
    annotated_frame = results[0].plot()

    try:
        boxes = results[0].boxes
        detected = boxes is not None and len(boxes) > 0
    except Exception:
        detected = False

    if detected and not alert_sent:
        try:
            snapshot_path = os.path.join('results', 'live_video_alert.jpg')
            cv2.imwrite(snapshot_path, annotated_frame)
            send_alert_image(
                snapshot_path,
                'suhastms2004@gmail.com',
                subject='Immediate Detection Alert (Live Video)',
                body='Auto alert: detection found during live video processing.'
            )
            alert_sent = True
        except Exception:
            pass

    # Display the frame with detections
    cv2.imshow("YOLO Detection Output", annotated_frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video source and close OpenCV windows
cap.release()
cv2.destroyAllWindows()
