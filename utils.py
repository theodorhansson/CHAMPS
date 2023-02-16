import matplotlib.pyplot as plt
import numpy as np
import time


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
        print(f"Warning: Unused parameter {Extra_parameters}{source_func}")

    elif Missing_parameters != set():
        raise Exception(f"Missing parameters {Missing_parameters}{source_func}")


def optional_arguments_merge(config: dict = dict(), optional_default=dict()):
    # Merges config and optional dicts. Value in config overwrites default
    out_dict = optional_default
    out_dict.update(config)
    return out_dict


def interval_2_points(specification: list[list]) -> list[list]:
    # Takes in list [[A, x, B],[C, y, D]] and returns a list of all points
    # in specified intervals where A, B are start and end, and x step size.
    # Output like: [[A, A+x, ..., B], [C, C+y, ..., D]]

    if type(specification[0]) != list:
        print(f"Warning: Interval specification {specification} not list of lists.")
        if len(specification) == 3:
            print("Attempting inteval fix.")
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
        sub_interval = np.arange(start, end, delta)
        points.append(sub_interval)
    return points


def ramp_current(DC_supply, start, stop, step=10):
    # Ramps up/down current to/from given values for a supplied DC_unit
    current_steps = np.linspace(start, stop, step)

    for current in current_steps:
        DC_supply.set_current(current)
        time.sleep(50 * 1e-3)  # 50 ms


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
    # Some tests

    test_dict = {
        "ABC": "EFG",
        "HI": {"JK": "HK"},
        "volTage": 10,
        "A": {"B": {"C": {"D": 7}}},
        "78": 12,
        "12A": "abc",
    }
    opt_dict = {"12A": "ABC", "CTH": "KTH"}

    argument_checker(test_dict, ["ABC"], optional_config=opt_dict)

    # interval = [[1, 0.1, 3]]

    # print(interval_2_points(interval))

    # conf = {"type": "chalmers", "abc": "123", "petg": 111}
    # opt = {"petg": 222, "PPP": "ASDASD"}
    # print(optional_arguments_merge(conf, opt))

    # plot = AnimatedPlot("A", "B", "C")
    # plot.add_point(1, 2)
    # plot.add_point(3, 2)
    # plot.keep_open()
