import matplotlib.pyplot as plt
import json


def plot_track(
    track: list[tuple[float, float]], track_id: int, axis_to_plot: str, path: str = None
) -> None:
    """Plot the trajectory of a tracked object."""
    x_coords, y_coords = zip(*track)
    if axis_to_plot == "x":
        data = x_coords
        ylabel = "X Coordinate"
    elif axis_to_plot == "y":
        data = y_coords
        ylabel = "Y Coordinate"
    else:
        raise ValueError("axis_to_plot must be 'x' or 'y'")

    plt.plot(data, marker="o", label=f"Track ID {track_id}")
    plt.xlabel("Frame")
    plt.ylabel(ylabel)
    plt.title("Object Trajectory")
    plt.legend()
    plt.grid()

    if path:
        plt.savefig(path)
    else:
        plt.show()
