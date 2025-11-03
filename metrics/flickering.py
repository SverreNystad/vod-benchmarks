import matplotlib.pyplot as plt
import json


def plot_track(
    track: list[tuple[float, float]], track_id: int, axis_to_plot: str
) -> None:
    """Plot the trajectory of a tracked object."""
    x_coords, y_coords = zip(*track)
    if axis_to_plot == "x":
        data = x_coords
    elif axis_to_plot == "y":
        data = y_coords
    else:
        raise ValueError("axis_to_plot must be 'x' or 'y'")

    plt.plot(data, marker="o", label=f"Track ID {track_id}")
    plt.xlabel("Frame")
    plt.ylabel("Coordinate")
    plt.title("Object Trajectory")
    plt.legend()
    plt.grid()
    plt.show()


if __name__ == "__main__":
    with open("yolo11n_webcam_track_history.json", "r") as f:
        track_history = json.load(f)

    plot_track(
        track_history["96"], track_id=0, axis_to_plot="x"
    )  # Example for track ID 0
