from metrics.flickering import plot_track
import json

with open("metrics/yolo11n_webcam_track_history.json", "r") as f:
    track_history = json.load(f)


plot_track(
    track=track_history["96"],
    value_to_plot="width",
    path="experiments/track_96_width_coordinates.png",
)
