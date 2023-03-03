import matplotlib.pyplot as plt
import numpy as np
import time
import warnings
import math


def argument_checker(
    config: dict,
    expected_keys: list,
    optional_config: dict = dict(),
    warn_extra=True,
    source_func="",
):
    # Behavior:
    # Checks if supplied dict contains required keys
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


def list_number_recaster(input: list | float) -> list | float:
    # Recursivly tries to convert strings to floats in a list
    # [1, "2"] -> [1, 2]
    if type(input) == float or type(input) == int:
        output = input
    elif type(input) == str:
        output = float(input)
    elif type(input) == list or type(input) == tuple:
        output = []
        for element in input:
            output.append(list_number_recaster(element))

        # Recast to tuple if input
        if type(input) == tuple:
            output = tuple(output)

    return output


def interval_2_points(specification: list[list]) -> list:
    # Takes in list [[A, x, B], [C, y, D], P] and returns a list of points.
    # Output: [[A, A+x, ..., B], [C, C+y, ..., D], [P]]
    # Also accepts single point outside of list P -> [[P]]

    # Convert strings to floats if possible
    specification = list_number_recaster(specification)

    if type(specification) == float or type(specification) == int:
        # Handles case where specification is number
        out_list = [[specification]]
        return out_list
    elif type(specification) != list:
        raise TypeError(
            f"Interval specification {specification} neither list nor number"
        )

    points = []
    for sub_specification in specification:
        if type(sub_specification) == float or type(sub_specification) == int:
            sub_interval = [sub_specification]
        elif type(sub_specification) == list:
            if len(sub_specification) != 3:
                # Check if every sub-interval specified correct
                raise TypeError(
                    f"Interval sub-specification {sub_specification} not length 3."
                )

            # Extract the values
            start = sub_specification[0]
            delta = sub_specification[1]
            end = sub_specification[2]

            for value in (start, delta, end):
                # Check if they are valid type
                if type(value) != float and type(value) != int:
                    raise TypeError(
                        f"Interval sub-specification {sub_specification} component {value} not number"
                    )

            if start == end:
                # If start and end are same point, don't create duplicate
                sub_interval = [start]
            elif abs(start - end) <= delta:
                # If points are too close, add them anyways
                sub_interval = [start, end]
            else:
                # Create arranged list if nothing special
                sub_interval = list(np.arange(start, end, delta))

            # Post-processing
            if end not in sub_interval:
                # Add end point if not in specification
                sub_interval.append(end)

        else:
            raise TypeError(
                f"Interval sub-specification {sub_specification} in specification {specification} neither list nor number"
            )

        # Add sub_interval to point result
        points.append(sub_interval)
    return points


def ramp_current(DC_supply, start, stop, step=10):
    # Ramps up/down current to/from given values for a supplied DC_unit
    current_steps = np.linspace(start, stop, step)

    # If start and stop are same, skip ramp
    if start == stop:
        return None

    for current in current_steps:
        DC_supply.set_current(current)
        time.sleep(50 * 1e-3)  # 50 ms


def dict_2_lower(indict: dict) -> dict:
    # Recursive dict to lower function
    out_dict = dict()
    for key in indict:
        value = indict[key]
        out_key = key.lower() if type(key) == str else key

        if type(value) == dict:
            temp = dict_2_lower(value)
            out_dict[out_key] = temp

        else:
            out_value = value.lower() if type(value) == str else value
            out_dict[out_key] = out_value
    return out_dict


def create_save_list(result_dict: dict) -> tuple[list[list], str]:
    result_matrix = []
    keys = list(result_dict.keys())
    no_of_points = len(result_dict[keys[0]])  # How many rows there are

    if no_of_points == 0:
        print("No data to save. Probably Ctrl+C too early.")
        return [], ""  # Probably bad error behavior

    for i in range(no_of_points):
        row = []
        for key in keys:
            item = result_dict[key][i]

            if type(item) is list:
                row += item
            else:
                row.append(item)
        result_matrix.append(row)

    result_headers = []
    for key in keys:
        data = result_dict[key][0]

        length = ""
        if type(data) is list:
            length = "(" + str(len(data)) + ")"

        result_headers.append(key + length)
    header_string = " ".join(result_headers)

    return result_matrix, header_string


def closest_matcher(
    data: float,
    accepted_vals: list,
    round_type: str = "up",
    msg: str = "",
):
    # Function checks if value is accepted, and tries to round it if possible

    # If string, recast to number
    data = list_number_recaster(data)
    accepted_vals = list_number_recaster(accepted_vals)

    if msg:
        # Set message if not empty
        msg = " in " + msg

    max_val = max(accepted_vals)
    min_val = min(accepted_vals)

    # If exact mode enabled, rasie exception if not in set
    if round_type.lower() == "exact" and data not in accepted_vals:
        raise Exception(
            f"{data} not a valid value{msg}. Please pick among {accepted_vals}."
        )

    # If data bigger than all accepted
    elif data > max_val:
        print(f"Warning: {data} larger than accepted{msg}, using {max_val} instead.")
        return max_val
    elif data < min_val:
        print(f"Warning: {data} smaller than accepted{msg}, using {min_val} instead.")
        return min_val

    # If not in list, round up to closest value in list
    elif data not in accepted_vals:

        match round_type.lower():
            case "up":
                custom_key = lambda x: math.inf if x - data < 0 else x - data
            case "down":
                custom_key = lambda x: math.inf if x - data > 0 else data - x
            case "regularly":
                custom_key = lambda x: abs(x - data)
            case _:
                raise Exception(
                    f"closest_matcher unknown round_type {round_type}{msg} detected."
                )
        data_old = data
        data = min(accepted_vals, key=custom_key)
        print(
            f"Warning: {data_old} not accepted{msg}, rounding {round_type} to {data}."
        )
        return data

    # Return the same if nothing changed
    else:
        return data


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
