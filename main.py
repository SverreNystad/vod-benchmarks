from metrics.flickering import plot_track
import json

with open("metrics/yolo11n_webcam_track_history.json", "r") as f:
    track_history = json.load(f)


plot_track(
    track=track_history["2"],
    value_to_plot="y",
    path="experiments/yolo/flickering/y_track_2.png",
)
