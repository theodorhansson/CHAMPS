import pyvisa

# import utils
import time
import numpy as np
import math

_required_arguments = ["gpib_address", "type"]
_optional_arguments = {"reference_level_dbm": -40, "display_level_scale_dbm": 10}

# Many comments in methods from "MS9710B Optical Spectrum Analyzer Remote Control Operation Manual", ANRITSU 2007
### Read manual page 139, 261 for commands ###

# TODO: Better typecheck?


class SpectrumAnalyzer:
    def __init__(self, config_dict: dict, resource_manager: object = None):
        utils.argument_checker(config_dict, _required_arguments, _optional_arguments)

        config_dict = utils.optional_arguments_merge(config_dict, _optional_arguments)
        self.address = str(config_dict["gpib_address"])
        self.interface_ID = "GPIB0"
        self.conn_str = self.interface_ID + "::" + self.address

        self.reference_level_dBm = config_dict["reference_level_dbm"]
        self.display_level_scale_dBm = config_dict["display_level_scale_dbm"]

        # Use parent resource manager if exists
        if resource_manager != None:
            self.resource_manager = resource_manager
        else:
            self.resource_manager = pyvisa.ResourceManager()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.close()

    def open(self):  # TODO: move to __init__?
        # Define instrument with pyvisa
        self.instrument = self.resource_manager.open_resource(self.conn_str)

        # Due to big datatransfers, instrument timeout must be increased
        self.instrument.timeout = 2000  # ms. It takes 1s for 5001 samples
        self.instrument.read_termination = "\r\n"
        self.instrument.write_termination = "\r\n"

        self.set_ref_level_dBm(self.reference_level_dBm)
        self.set_level_scale_dBm(self.display_level_scale_dBm)
        self.set_time()

    def close(self):
        # Exit instrument
        self.instrument.close()

    def set_time(self):
        date = time.strftime(rf"%y,%m,%d")
        clock = time.strftime(rf"%H,%M")
        self.instrument.write("DATE " + date)
        self.instrument.write("TIME " + clock)

    def set_avg_factor(self, avg_factor: int | str):
        # Sets the number of points for point averaging.
        # Data range 2<= n <= 1000, or "OFF"
        GPIB_write = "AVT " + str(avg_factor)
        self.instrument.write(GPIB_write)

    def get_avg_factor(self) -> str:
        GPIB_write = "AVT?"
        avg = self.instrument.query(GPIB_write)
        return avg

    def set_center_wavelength_nm(self, center_wl: float):
        # Sets a center wavelength. The unit is always nm.
        # Input value down to the second decimal place. Data range: 600 <= n <= 1750
        GPIB_write = "CNT " + str(round(center_wl, 2))
        self.instrument.write(GPIB_write)

    def get_center_wavelength_nm(self) -> float:
        GPIB_write = "CNT?"
        center_wl = self.instrument.query(GPIB_write)
        return float(center_wl)

    def set_level_scale_dBm(self, level_scale: float):
        # Selects a log scale as a level scale and sets a scale value (dB/div)
        # Data range: 0.1 <= level_scale <= 10.0
        GPIB_write = "LOG " + str(round(level_scale, 1))
        self.instrument.write(GPIB_write)

    def get_level_scale(self) -> str:
        # Returns whether a log or linear scale is set as a level scale.
        GPIB_write = "LVS?"
        scale_type = self.instrument.query(GPIB_write)
        return scale_type

    def set_linear_resolution_nm(self, resolution: float):
        # n indicates measurement resolution. The unit is always nm.
        # input one of the following values: 1.0, 0.5, 0.2, 0.1, 0.07, 0.05
        GPIB_write = "RES " + str(resolution)
        self.instrument.write(GPIB_write)

    def get_linear_resolution_nm(self) -> float:
        GPIB_write = "RES?"
        resolution = self.instrument.query(GPIB_write)
        return float(resolution)

    def set_sample_points(self, n_points: int):
        # # Sets the sampling point for measurement. ****: 11 to 20001 (1 step), 0(auto)
        # 251, 501, 1001, 2001, 5001
        GPIB_write = "MPT " + str(n_points)
        self.instrument.write(GPIB_write)

    def get_sample_points(self) -> int:
        GPIB_write = "MPT?"
        n_points = self.instrument.query(GPIB_write)
        return int(n_points)

    def set_ref_level_dBm(self, level: float):
        # TODO: BROKEN
        # NOTE: Perhaps doesn't need implement?
        # Sets the reference level. [in LOG] (Unit: dBm), ***.***: -190.000 to 50.000 (0.1 step)
        return
        GPIB_write = "MKD " + str(level) + " DBM"
        self.instrument.write(GPIB_write)

    def get_ref_level(self):
        GPIB_write = "MKD?"
        n_points = self.instrument.query(GPIB_write)
        return n_points

    def set_sensitivity(self, sensitivity_id: str):
        pass

    def get_sensitivity(self):
        return ""

    def set_wavelength_span_nm(self, span: float):
        # Sets the span. (Unit_ nm), ****.*: 0, 0.5 to 1200.0 (0.1 step)
        GPIB_write = "SPN " + str(round(span, 1))
        self.instrument.write(GPIB_write)

    def get_wavelength_span(self) -> float:
        GPIB_write = "SPN?"
        span = self.instrument.query(GPIB_write)
        return float(span)

    def get_wavelength_axis(self) -> list[float]:

        span = self.get_wavelength_span()
        samplepoints = self.get_sample_points()
        center = self.get_center_wavelength_nm()
        start = center - (span / 2)
        stop = center + (span / 2)

        return list(np.linspace(start, stop, samplepoints))

    def get_intensity_data_A_dBm(self):
        # Outputs dB measurement data equivalent to the number of sampling points from memory A.

        # Sometimes misinterprets bytes in stream as end of message
        r_term = self.instrument.read_termination
        self.instrument.read_termination = ""

        GPIB_write = "DBA?"
        self.instrument.write(GPIB_write)
        try:
            databytes = self.instrument.read_raw()
        except:
            raise Exception(
                "Something went wrong when reading data from Anritsu. Did you already empty the buffer?"
            )

        databytes = databytes[:-2]  # Last two bytes are \r\n, remove them

        no_of_shorts = int(len(databytes) / 2)  # 2 bytes make a short.
        intensities_dB = []

        for i in range(no_of_shorts):
            byte1 = databytes[2 * i]
            byte2 = databytes[2 * i + 1]

            # This is ugly but superfast!
            # First bit in b1 is sign, so remove that by a bitwise &.
            # Then left shift 8 steps to make b1 the first 8 bits of total 16.
            # Then add b2 to this (puts them in the 8 last bits).
            # Finally remove the value of *only* the first bit in (b1 << 8), since this
            # bit is equal to *negative* its normal value.

            # Ex: byte1 = 233 (11101001) , byte2 = 162 (10100010)
            # 11101001 -> 01101001 -> 01101001 00000000 -> 01101001 10100010 ->
            # -> 01101001 10100010 minus 10000000 00000000 = -5726

            ans = ((byte1 & 0b01111111) << 8) + byte2 - ((byte1 & 0b10000000) << 8)
            ans *= 0.01  # 9832 -> 98.32 dB
            intensities_dB.append(ans)

        self.instrument.read_termination = r_term
        return intensities_dB

    def get_connected_visa_devices(self):
        return self.resource_manager.list_resources()

    def get_sweep_status(self) -> int:  # NOTE: use "MOD" instead
        # Gets the current status of instrument from event register
        # Status codes for anritsu:
        # 0: A spectrum is not being measured.
        # 1: A spectrum is being measured (single sweep).
        # 2: A spectrum is being measured (repeat sweep).
        # 3: Power monitor

        GPIB_write = "MOD?"
        status = self.instrument.query(GPIB_write)
        return int(status)

    def _start_single_sweep(self):
        # Starts a scan in mode "single"
        GPIB_write = "SSI"
        self.instrument.write(GPIB_write)

    def do_single_scan(self):
        # starts single and holds thread until done
        stop_code = 0  # This value indicates finished
        stop = None

        # Start measurment and check if finished in loop
        self._start_single_sweep()
        while stop != stop_code:
            time.sleep(0.5)
            stop = self.get_sweep_status()


def closest_matcher(
    data: float,
    accepted_vals: list,
    round_type: str = "up",
    msg: str = "",
):
    # Function checks if value is accepted, and tries to round it if possible

    if msg:
        # Set message if not empty
        msg = " in " + msg

    max_val = max(accepted_vals)
    if data > max_val:
        # If data bigger than all accepted
        print(f"Warning: {data} larger than accepted{msg}, using {max_val} instead.")
        return max_val

    elif data not in accepted_vals:
        # If not in list, round up to closest value in list

        match round_type.lower():
            case "up":
                custom_key = lambda x: math.inf if x - data < 0 else x - data
            case "down":
                custom_key = lambda x: math.inf if x - data > 0 else data - x
            case "regularly":
                custom_key = lambda x: x - data
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
    else:
        return data


def test_OSA():
    test_config = {"gpib_address": 12, "type": "jiopfjio"}

    OSA = SpectrumAnalyzer(test_config)
    OSA.open()

    print(OSA.get_center_wavelength_nm())
    OSA.set_center_wavelength_nm()
    print(OSA.get_center_wavelength_nm())

    OSA.close()


def test_jioasd():
    accepted_val = [51, 101, 251, 501, 1001, 2001, 5001]
    n_points = 551

    A = closest_matcher(n_points, accepted_val, msg="hej hej", round_type="regularly")
    print(A)


if __name__ == "__main__":
    # test_OSA()
    test_jioasd()
