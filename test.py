from ultralytics import YOLO
import cv2

# Load the YOLO model
model = YOLO(r"besthello.pt")

# Run predictions on the video
results = model.predict(source="0", show=True)

# Print the results
print(results)
