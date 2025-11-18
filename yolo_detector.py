import cv2
import numpy as np

from ultralytics import YOLO


model = YOLO("yolo11l.pt")
path = "../data/pohang/sequence.mp4"
cap = cv2.VideoCapture(path)
frame_number = 0
while cap.isOpened():
    success, frame = cap.read()
    if success:
        results = model.predict(frame)
        annotated_frame = results[0].plot()
        cv2.imshow("YOLO11 Detection", annotated_frame)
        cv2.imwrite(f"experiments/yolo/detection/{frame_number}.png", annotated_frame)
        frame_number += 1
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break
cap.release()
cv2.destroyAllWindows()
