from collections import defaultdict

import cv2
import numpy as np

from ultralytics import YOLO

import json

model = YOLO("yolo11l.pt")
path = "../data/pohang/sequence.mp4"
cap = cv2.VideoCapture(path)
# cap = cv2.VideoCapture(0)  # Open the default webcam
track_history = defaultdict(lambda: [])

while cap.isOpened():
    success, frame = cap.read()
    if success:
        results = model.track(frame, persist=True)
        boxes = results[0].boxes.xywh.cpu()
        if results[0].boxes.id is None:
            track_ids = []
        else:
            track_ids = results[0].boxes.id.int().cpu().tolist()
        annotated_frame = results[0].plot()
        for box, track_id in zip(boxes, track_ids):
            x, y, w, h = box
            track = track_history[track_id]
            track.append((float(x), float(y), float(w), float(h)))
            points = np.hstack((track)).astype(np.int32).reshape((-1, 1, 2))
            cv2.polylines(
                annotated_frame,
                [points],
                isClosed=False,
                color=(230, 230, 230),
                thickness=10,
            )
        cv2.imshow("YOLO11 Tracking", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break
cap.release()
cv2.destroyAllWindows()

with open("metrics/yolo11l_webcam_track_history.json", "w") as f:
    json.dump(dict(track_history), f)
