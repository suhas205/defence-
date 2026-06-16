import cv2
import time
import os
from ultralytics import YOLO
from mail import send_alert_image
import sys
try:
    import winsound
except Exception:
    winsound = None

MODEL_PATHS = {
    "Normal": r"C:\Users\suhas_t9klwz0\Downloads\best (1).pt",
    "SAR": r"C:\SUHAS_P\defence pro\ship.pt"
}

# Determine model path/type from CLI
if len(sys.argv) > 1:
    arg = sys.argv[1]
    if arg in MODEL_PATHS:  # passed model type
        model_path = MODEL_PATHS[arg]
    else:
        model_path = arg  # assume explicit path
else:
    model_path = MODEL_PATHS["Normal"]

# Load YOLO model
model = YOLO(model_path)
os.makedirs('results', exist_ok=True)

# Initialize video capture (0 for the default camera)
cap = cv2.VideoCapture(0)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Unable to access the camera.")
    exit()

# Desired frames per second (FPS)
desired_fps = 5
frame_interval = 1 / desired_fps

print("Starting live detection. Press 'q' to quit.")
alert_sent = False
last_beep = 0.0
beep_cooldown_s = 1.0

# Main loop for live detection
while cap.isOpened():
    start_time = time.time()  # Record start time for frame processing

    # Read a frame from the camera
    ret, frame = cap.read()
    if not ret:
        print("Error: Unable to read from the camera.")
        break

    # Run YOLO model on the frame
    results = model(frame)

    # Annotate the frame with the detection results
    annotated_frame = results[0].plot()

    detected = False
    try:
        boxes = results[0].boxes
        detected = boxes is not None and len(boxes) > 0
    except Exception:
        detected = False

    if detected and winsound is not None:
        now = time.time()
        if now - last_beep >= beep_cooldown_s:
            try:
                winsound.Beep(1000, 200)
            except Exception:
                pass
            last_beep = now

    if detected and not alert_sent:
        try:
            snapshot_path = os.path.join('results', 'live_alert.jpg')
            cv2.imwrite(snapshot_path, annotated_frame)
            send_alert_image(
                snapshot_path,
                'suhastms2004@gmail.com',
                subject='Immediate Detection Alert (Live Camera)',
                body='Auto alert: detection found in live camera.'
            )
            alert_sent = True
        except Exception:
            pass

    # Display the annotated frame
    cv2.imshow("Live Detection", annotated_frame)

    # Calculate the elapsed time and wait to maintain desired FPS
    elapsed_time = time.time() - start_time
    time_to_wait = frame_interval - elapsed_time
    if time_to_wait > 0:
        time.sleep(time_to_wait)

    # Break the loop when the user presses 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exiting live detection...")
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
print("Resources released. Detection terminated.")
