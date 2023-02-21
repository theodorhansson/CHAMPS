import pyvisa
from utils import argument_checker

_required_arguments = ["gpib_address", "type"]


class keithley2400:
    def __init__(self, config_dict: dict, resource_manager: object = None):
        argument_checker(config_dict, _required_arguments, source_func="keithley")
        self.address = str(config_dict["gpib_address"])
        self.interface = "GPIB0"

        # Use parent resource manager if exists
        if resource_manager != None:
            self.resource_manager = resource_manager
        else:
            self.resource_manager = pyvisa.ResourceManager()

    def get_voltage(self) -> float:
        ans = self.instrument.query(":READ?")
        ans = ans.split(",")[0]  # First item is voltage
        return float(ans)

    def set_voltage_limit(self, volts: float):
        self.instrument.write(":SENSE:VOLTAGE:DC:PROTECTION " + str(volts))

    def set_current(self, current: float):
        current = current * 1e-3  # mA to A
        self.instrument.write(":SOURCE:CURRENT " + str(current))

    def get_current(self) -> float:
        ans = self.instrument.query(":READ?")
        current = ans.split(",")[1]  # Second item is current
        current = float(current) * 1e3  # A to mA
        return current

    def get_voltage_and_current(self) -> list[float]:
        ans = self.instrument.query(":READ?")
        data = ans.split(",")[0:2]  # [volt, current, unknown, unknown]
        data = [float(x) for x in data]
        data[1] = data[1] * 1e3  # A to mA
        return data  # [volt, mA]

    def set_output(self, state: bool):
        self.instrument.write(":OUTPUT " + str(int(state)))

    def open(self):  # TODO: Rename to open_current?
        # Define where instrument is
        conn_str = self.interface + "::" + self.address  # like GPIB0::24

        # Open and create instrument class
        rm = pyvisa.ResourceManager()
        self.instrument = rm.open_resource(conn_str)

        # Initialize current mode
        self.instrument.write(":SOURCE:FUNCTION CURRENT")
        self.instrument.write(":SOURCE:CURRENT:MODE FIXED")
        self.instrument.write(":SOURCE:CURRENT:RANGE:AUTO 1")

        # Sets what the display shall show
        self.instrument.write(":SENSE:FUNCTION 'VOLT'")

        self.instrument.write(":SENSE:VOLT:RANGE:AUTO 1")

    def close(self):
        self.instrument.close()


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
