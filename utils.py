import matplotlib.pyplot as plt
import numpy as np


def argument_checker(config: dict, expected_keys: list):
    # Behavior:
    # If extra parameter is found, warn user but continue program
    # If parameter missing, raise exception

    config_values = set(config.keys())
    expected_set = set(expected_keys)

    Extra_parameters = config_values - expected_set
    Missing_parameters = expected_set - config_values

    if Extra_parameters != set() and Missing_parameters != set():
        raise Exception(
            f"Extra parameter {Extra_parameters} and missing parameter {Missing_parameters} detected."
        )

    elif Extra_parameters != set():
        print(f"Warning: Unused parameter {Extra_parameters}")

    elif Missing_parameters != set():
        raise Exception(f"Missing parameters {Missing_parameters}")


def interval_2_points(specification: list[list]) -> list:
    # Takes in list [[A, x, B],...] and returns a list of all points
    # in specified intervals where A, B are start and end, and x step size

    if type(specification[0]) != list:
        print(f"Warning: Interval specification {specification} not list of lists.")
        # Fix error not list of list
        specification = [specification]

    points = []
    for pairs in specification:
        if type(pairs) != list:
            # Checks if sublist is list
            raise Exception(f"Interval sub-specification {pairs} not list")
        elif len(pairs) != 3:
            # Check if every sub-interval specified correct
            raise Exception(f"Interval sub-specification {pairs} not length 3.")

        start = pairs[0]
        delta = pairs[1]
        end = pairs[2]
        sub_interval = np.arange(start, end, delta)
        points.append(sub_interval)
    return points


class AnimatedPlot:
    # Used to dynamically add datapoints
    def __init__(
        self, x_label: str, y_label: str, title: str, enable_grid: bool = False
    ):
        self.plot = plt.ion()
        self.ax = plt.subplot(111)

        self.ax.set_title(title)
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.ax.grid(enable_grid)

    def add_point(self, x: float, y: float):
        # Adds point and updates figure
        self.ax.scatter(x, y)
        plt.draw()
        plt.pause(0.0001)

    def keep_open(self):
        # Keeps plot open
        plt.ioff()  # Turn off interactive
        plt.show()


if __name__ == "__main__":

    test_dict = {
        "ABC": "EFG",
        "HI": {"JK": "HK"},
        "volTage": 10,
        "A": {"B": {"C": {"D": 7}}},
        "78": 12,
        "12A": "abc",
    }

    argument_checker(test_dict, ["ABC"])

    interval = [[1, 0.1, 3]]

    print(interval_2_points(interval))

    plot = AnimatedPlot("A", "B", "C")
    plot.add_point(1, 2)
    plot.add_point(3, 2)
    plot.keep_plot()
    print("hi")
