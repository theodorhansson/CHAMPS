import pyvisa
import utils
import time

_required_arguments = ["gpib_address", "type"]
_optional_arguments = {"verbose_printing": 0}


class keithley2400:
    def __init__(self, config_dict: dict, resource_manager: object = None):
        utils.argument_checker(
            config_dict,
            _required_arguments,
            _optional_arguments,
            source_func="keithley",
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

        print("__init__() in keithley2400") if self.verbose & 4 + 8 else None

    def __enter__(self):
        print("__enter__() in keithley2400") if self.verbose & 8 else None
        self.open()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        time.sleep(0.1)  # Short wait in case of exception
        if self.verbose & 8:
            print("__exit__() in keithley2400")
            print(f"{exception_type=}, {exception_value=}, {exception_traceback=}")

        utils.ramp_current(self, self.get_current(), 0)
        self.set_current(0)

        self.set_output(False)
        self.close()

    def open(self):  # TODO: Rename to open_current?
        # Define where instrument is
        print("enter() in keithley2400") if self.verbose & 8 else None

        conn_str = self.interface + "::" + self.address  # like GPIB0::24

        # # Error check
        # connected_devices = self.resource_manager.list_resources()
        # connected_devices = [device.lower() for device in connected_devices]
        # if conn_str.lower() + "::instr" not in connected_devices:
        #     print(f"List of connected GPIB devices: {connected_devices}")
        #     raise ConnectionError(
        #         f"Keitley2400 connection failed using address {conn_str}."
        #     )

        # Open and create instrument class
        self.instrument = self.resource_manager.open_resource(conn_str)

        # Initialize current mode
        self.instrument.write(":SOURCE:FUNCTION CURRENT")
        self.instrument.write(":SOURCE:CURRENT:MODE FIXED")
        self.instrument.write(":SOURCE:CURRENT:RANGE:AUTO 1")

        # Sets what the display shall show
        self.instrument.write(":SENSE:FUNCTION 'VOLT'")

        self.instrument.write(":SENSE:VOLT:RANGE:AUTO 1")

    def close(self):
        print("close() in keithley2400") if self.verbose & 8 else None
        self.instrument.close()

    def get_voltage(self) -> float:
        ans = self.instrument.query(":READ?")
        ans = ans.split(",")[0]  # First item is voltage

        if self.verbose & 8:
            print(f"get_voltage() in keithley2400: value {ans}")
        return float(ans)

    def set_voltage_limit(self, volts: float):
        if self.verbose & 8:
            print(f"set_voltage_limit() in keithley2400: setting to {volts}")

        self.instrument.write(":SENSE:VOLTAGE:DC:PROTECTION " + str(volts))

    def set_current(self, current: float):
        if self.verbose & 8:
            print(f"set_current() in keithley2400: setting to {current}")

        current = current * 1e-3  # mA to A
        self.instrument.write(":SOURCE:CURRENT " + str(current))

    def get_current(self) -> float:
        ans = self.instrument.query(":READ?")
        current = ans.split(",")[1]  # Second item is current
        current = float(current) * 1e3  # A to mA

        if self.verbose & 8:
            print(f"get_current() in keithley2400: value {current}")
        return current

    def get_voltage_and_current(self) -> list[float]:
        ans = self.instrument.query(":READ?")
        data = ans.split(",")[0:2]  # [volt, current, unknown, unknown]
        data = [float(x) for x in data]
        data[1] = data[1] * 1e3  # A to mA

        if self.verbose & 8:
            print(f"get_voltage_and_current() in keithley2400: values {data}")
        return data  # [volt, mA]

    def set_output(self, state: bool):
        # Toggle kethley output on/off
        if self.verbose & 4 + 8:
            if state:
                print("set_output() in keithley2400: Enabling")
            else:
                print("set_output() in keithley2400: Disabling")

        self.instrument.write(":OUTPUT " + str(int(state)))


def performance_test():
    # Test to determine how fast keithley is for different operations
    import time

    N = 50

    config = {"gpib_address": 24, "type": "jipsdf"}
    Keith = keithley2400(config)
    Keith.open()
    Keith.set_output(True)

    time.sleep(0.1)
    t_start = time.time()
    for _ in range(N):
        Keith.set_current(0)
    t_end = time.time()
    t_per = (t_end - t_start) / N
    print(f"Time per set_current {t_per}")

    time.sleep(0.1)
    t_start = time.time()
    for _ in range(N):
        Keith.get_current()
    t_end = time.time()
    t_per = (t_end - t_start) / N
    print(f"Time per get_current {t_per}")

    time.sleep(0.1)
    t_start = time.time()
    for _ in range(N):
        Keith.get_voltage()
    t_end = time.time()
    t_per = (t_end - t_start) / N
    print(f"Time per get_voltage {t_per}")

    time.sleep(0.1)
    t_start = time.time()
    for _ in range(N):
        Keith.get_voltage_and_current()
    t_end = time.time()
    t_per = (t_end - t_start) / N
    print(f"Time per get_voltage_and_current {t_per}")

    time.sleep(0.1)
    t_start = time.time()
    for _ in range(N):
        Keith.set_current(0)
        Keith.get_voltage()
        Keith.get_current()
    t_end = time.time()
    t_per = (t_end - t_start) / N
    print(f"Time per full old loop {t_per}")

    time.sleep(0.1)
    t_start = time.time()
    for _ in range(N):
        Keith.set_current(0)
        Keith.get_voltage_and_current()
    t_end = time.time()
    t_per = (t_end - t_start) / N
    print(f"Time per full new loop {t_per}")

    Keith.set_output(False)
    Keith.close()


if __name__ == "__main__":
    performance_test()
