import pyvisa
import time

# Dumb code to import utils
try:
    import utils
except:
    import sys, pathlib

    util_path = str(pathlib.Path(__file__).parent.parent.resolve())
    sys.path.append(util_path)
    import utils

_required_arguments = ["gpib_address", "type"]
_optional_arguments = {"verbose_printing": 0}


class hamamatsu_s2281:
    def __init__(self, config_dict: dict, resource_manager: object = None):
        utils.argument_checker(
            config_dict,
            _required_arguments,
            _optional_arguments,
            source_func="diode_detector",
        )
        config_dict = utils.optional_arguments_merge(config_dict, _optional_arguments)

        self.address = str(config_dict["gpib_address"])
        self.interface = "GPIB0"
        self.verbose = config_dict["verbose_printing"]

        # Use parent resource manager if exists
        if resource_manager != None:
            self.resource_manager = resource_manager
        else:
            self.resource_manager = pyvisa.ResourceManager()

        print("__init__() in diode_detector") if self.verbose & 4 + 8 else None

    def __enter__(self):
        print("__enter__() in diode_detector") if self.verbose & 8 else None
        self.open()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        time.sleep(0.1)  # Short wait in case of exception
        if self.verbose & 8:
            print("__exit__() in diode_detector")
            print(f"{exception_type=}, {exception_value=}, {exception_traceback=}")

        utils.ramp_current(self, self.get_current(), 0)
        self.set_current(0)

        self.set_output(False)
        self.close()

    def open(self):  # TODO: Rename to open_current?
        # Define where instrument is
        print("enter() in diode_detector") if self.verbose & 8 else None

        conn_str = self.interface + "::" + self.address  # like GPIB0::24

        self.instrument = self.resource_manager.open_resource(conn_str)

        # Initialize current mode
        self.instrument.write(":SOURCE:FUNCTION CURRENT")
        self.instrument.write(":SOURCE:CURRENT:MODE FIXED")
        self.instrument.write(":SOURCE:CURRENT:RANGE:AUTO 1")

        # Sets what the display shall show
        self.instrument.write(":SENSE:FUNCTION 'VOLT'")

        self.instrument.write(":SENSE:VOLT:RANGE:AUTO 1")

    def close(self):
        print("close() in diode_detector") if self.verbose & 8 else None
        self.instrument.close()

    def get_voltage(self) -> float:
        ans = self.instrument.query(":READ?")
        ans = ans.split(",")[0]  # First item is voltage

        if self.verbose & 8:
            print(f"get_voltage() in diode_detector: value {ans}")
        return float(ans)

    def set_voltage_limit(self, volts: float):
        if self.verbose & 8:
            print(f"set_voltage_limit() in diode_detector: setting to {volts}")

        self.instrument.write(":SENSE:VOLTAGE:DC:PROTECTION " + str(volts))

    def set_current(self, current: float):
        if self.verbose & 8:
            print(f"set_current() in diode_detector: setting to {current}")

        current = current * 1e-3  # mA to A
        self.instrument.write(":SOURCE:CURRENT " + str(current))

    def get_current(self) -> float:
        ans = self.instrument.query(":READ?")
        current = ans.split(",")[1]  # Second item is current
        current = float(current) * 1e3  # A to mA

        if self.verbose & 8:
            print(f"get_current() in diode_detector: value {current}")
        return current

    def get_voltage_and_current(self) -> list[float]:
        ans = self.instrument.query(":READ?")
        data = ans.split(",")[0:2]  # [volt, current, unknown, unknown]
        data = [float(x) for x in data]
        data[1] = data[1] * 1e3  # A to mA

        if self.verbose & 8:
            print(f"get_voltage_and_current() in diode_detector: values {data}")
        return data  # [volt, mA]

    def set_output(self, state: bool):
        # Toggle kethley output on/off
        if self.verbose & 4 + 8:
            if state:
                print("set_output() in diode_detector: Enabling")
            else:
                print("set_output() in diode_detector: Disabling")

        self.instrument.write(":OUTPUT " + str(int(state)))


if __name__ == "__main__":
    pass
