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
frame_number = 0
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
            track.append((float(x), float(y)))

            if len(track) >= 2:
                track.pop(0)
            points = np.hstack((track)).astype(np.int32).reshape((-1, 1, 2))
            cv2.polylines(
                annotated_frame,
                [points],
                isClosed=False,
                color=(230, 230, 230),
                thickness=10,
            )
        cv2.imshow("YOLO11 Tracking", annotated_frame)
        cv2.imwrite(f"experiments/yolo/tracking/{frame_number}.png", annotated_frame)
        frame_number += 1
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break
cap.release()
cv2.destroyAllWindows()
