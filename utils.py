import matplotlib.pyplot as plt
import numpy as np
import time
import warnings


def argument_checker(
    config: dict,
    expected_keys: list,
    optional_config: dict = dict(),
    warn_extra=True,
    source_func="",
):
    # Behavior:
    # If extra parameter is found, warn user but continue program
    # If parameter missing, raise exception

    config_values = set(config.keys())
    expected_set = set(expected_keys)
    optional_set = set(optional_config.keys())
    total_accepted_set = expected_set | optional_set

    Extra_parameters = config_values - total_accepted_set
    Missing_parameters = expected_set - config_values

    if source_func:
        source_func = " in " + source_func

    if Extra_parameters != set() and Missing_parameters != set() and warn_extra:
        raise Exception(
            f"Extra parameter {Extra_parameters} and missing parameter {Missing_parameters} detected{source_func}."
        )

    elif Extra_parameters != set() and warn_extra:
        # print(f"Warning: Unused parameter {Extra_parameters}{source_func}")
        warnings.warn(f"Unused parameter {Extra_parameters}{source_func}", UserWarning)

    elif Missing_parameters != set():
        raise Exception  # (f"Missing parameters {Missing_parameters}{source_func}")


def optional_arguments_merge(config: dict = dict(), optional_default=dict()):
    # Merges config and optional dicts. Value in config overwrites default
    out_dict = optional_default
    out_dict.update(config)
    return out_dict


def interval_2_points(specification: list[list]) -> list:
    # Takes in list [[A, x, B],[C, y, D]] and returns a list of points.
    # Output: [[A, A+x, ..., B], [C, C+y, ..., D]]
    # Also accepts single value

    if type(specification) == float or type(specification) == int:
        # Handles case where specification is number
        out_list = [[specification]]
        return out_list

    elif (
        type(specification[0]) == float
        or type(specification[0]) == int
        and len(specification) == 1
    ):
        # Handles case where specification is number in list
        out_list = [[specification[0]]]
        return out_list

    elif type(specification[0]) != list:
        # print(f"Warning: Interval specification {specification} not list of lists.")
        if len(specification) == 3:
            # print("Attempting inteval fix.")
            # Fix error not list of list, by putting in list
            specification = [specification]
        else:
            raise Exception(
                f"Interval specification {specification} not list and not length 3."
            )

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

        if abs(start - end) <= delta:
            # Handles case where points are closer then shortest distance
            sub_interval = np.array([start, end])
        else:
            sub_interval = np.arange(start, end, delta)

        if end not in sub_interval:
            # Adds end point if not in interavl
            sub_interval = np.append(sub_interval, end)

        points.append(sub_interval)

    return points


def ramp_current(DC_supply, start, stop, step=10):
    # Ramps up/down current to/from given values for a supplied DC_unit
    current_steps = np.linspace(start, stop, step)

    for current in current_steps:
        DC_supply.set_current(current)
        time.sleep(50 * 1e-3)  # 50 ms


def signed_bits2int(input: str, endian="big") -> int:
    if endian == "small":  # Make big endian
        input = input[::-1]

    output = int(input[1:], 2)  # Select all normal bits and convert to int
    no_of_bits = len(input)
    if input[0] == "1":
        output -= 2 ** (no_of_bits - 1)  # The signed byte represents -2**15 in 16 bits
    return output


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
        # Adds point
        self.ax.scatter(x, y)

    def keep_open(self):
        # Keeps plot open
        plt.ioff()  # Turn off interactive
        plt.show()

    def update(self):
        plt.draw()
        plt.pause(0.0001)


if __name__ == "__main__":
    pass

    # plot = AnimatedPlot("A", "B", "C")
    # plot.add_point(1, 2)
    # plot.add_point(3, 2)
    # plot.keep_open()
