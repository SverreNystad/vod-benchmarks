from ultralytics import YOLO

# Load an official or custom model
model = YOLO("yolo11n.pt")  # Load an official Detect model

# Perform tracking with the model
# results = model.track("https://youtu.be/LNwODJXcvt4", show=True)  # Tracking with default tracker
results = model.track("https://www.youtube.com/watch?v=AlnHNi0hdO0", show=True, persist=True, tracker="bytetrack.yaml")  # with ByteTrack
