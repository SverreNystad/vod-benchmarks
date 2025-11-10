import matplotlib.pyplot as plt
import json


def plot_track(
    track: list[tuple[float, float, float, float]], value_to_plot: str, path: str = None
) -> None:
    """Plot the trajectory of a tracked object."""
    x_coords, y_coords, widths, heights = zip(*track)
    if value_to_plot == "x":
        data = x_coords
        ylabel = "X Coordinate"
    elif value_to_plot == "y":
        data = y_coords
        ylabel = "Y Coordinate"
    elif value_to_plot == "width":
        data = widths
        ylabel = "Width"
    elif value_to_plot == "height":
        data = heights
        ylabel = "Height"
    else:
        raise ValueError("axis_to_plot must be 'x' or 'y'")

    plt.plot(data, marker="o", label="Trajectory")
    plt.xlabel("Frame")
    plt.ylabel(ylabel)
    plt.title("Object Trajectory")
    plt.legend()
    plt.grid()

    if path:
        plt.savefig(path)
    else:
        plt.show()
