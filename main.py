from metrics.flickering import plot_track
import json

with open("metrics/yolo11n_webcam_track_history.json", "r") as f:
    track_history = json.load(f)


plot_track(
    track=track_history["96"],
    track_id=0,
    axis_to_plot="x",
    path="experiments/track_0_x_coordinates.png",
)
