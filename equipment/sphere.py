import win32com.client
import time
from utils import argument_checker

# OBS: en datastream ger en konstant växande lista med värden
# Based on python example from Ophir

# Avaliable ranges for IS6-D-UV
# 0    auto
# 1    1 W
# 2    300 mW
# 3    30 mW
# 4    3 mW
# 5    300 uW
# 6    30 uW
# 7    3 uW


_required_arguments = ["range", "min_measure_time"]


class INT_sphere:
    def __init__(self, config_dict: dict):
        argument_checker(config_dict, _required_arguments)
        self._OphirCOM = win32com.client.Dispatch("OphirLMMeasurement.CoLMMeasurement")
        DeviceList = self._OphirCOM.ScanUSB()
        Device = DeviceList[0]
        self._DeviceHandle = self._OphirCOM.OpenUSBDevice(Device)
        self._min_time = config_dict["min_measure_time"]

        # Set the default range
        default_range = config_dict["range"]
        self._OphirCOM.SetRange(self._DeviceHandle, 0, default_range)

    def open(self):
        # Start output stream
        self.set_output(True)

    def set_min_time(self, min_time: float):
        self._min_time = min_time

    def get_power(self):
        # Get reading from int. sphere
        time.sleep(self._min_time)
        data = self._OphirCOM.GetData(self._DeviceHandle, 0)
        # Checks if there is any data
        if len(data[0]) > 0:
            # Extract last power value from datastream
            power = data[0][-1]
            return power
        else:
            # print("Not connected/initialized")
            print("Get_power_none", data)
            return None  # TODO Decide what value should be here

    def set_range(self, newRange: int):
        # Set the measurement-range for the sphere
        self._OphirCOM.SetRange(self._DeviceHandle, 0, newRange)

    def get_ranges(self):
        # Return the possible ranges
        ranges = self._OphirCOM.GetRanges(self._DeviceHandle, 0)
        return ranges

    def set_output(self, state: bool):
        # Toggles reading from sphere
        if state:
            self._OphirCOM.StartStream(self._DeviceHandle, 0)
            # Wait for instrument to start
            for _ in range(10):
                data = self.get_power()
                print(data)
                if data != None:
                    break
                else:
                    # Wait for start
                    time.sleep(0.4)
        else:
            self._OphirCOM.StopStream(self._DeviceHandle, 0)

    def get_device_list(self):
        # Get list of connected devices
        return self._OphirCOM.ScanUSB()

    def get_device_handle(self):
        # Get name of current device_handle
        return self._DeviceHandle

    def close(self, exception_type, exception_value, exception_trace):
        # Stops and disconnects all OphirCOM
        self._OphirCOM.StopAllStreams()
        self._OphirCOM.CloseAll()

    def test(self):
        self._OphirCOM.StartStream(self._DeviceHandle, 0)
        for _ in range(10):
            time.sleep(0.2)  # wait a little for data
            data = self._OphirCOM.GetData(self._DeviceHandle, 0)
            if (
                len(data[0]) > 0
            ):  # if any data available, print the first one from the batch
                print(
                    "Reading = {0}, TimeStamp = {1}, Status = {2} ".format(
                        data[0][0], data[1][0], data[2][0]
                    )
                )
            else:
                print("no data")


def sphere_tests():
    test_dict = dict(range=3)
    SP = INT_sphere(test_dict)
    SP.set_output(True)
    dt = 0.1
    print("start loop")
    for _ in range(20):
        print(SP.get_power())
        time.sleep(dt)

    time.sleep(5)
    for _ in range(10):
        print(SP.get_power())
        time.sleep(dt)

    del SP

    # print(SP.test())


def sphere_tests2():
    test_dict = dict(range=3)
    SP = INT_sphere(test_dict)
    SP.test()


if __name__ == "__main__":
    sphere_tests()
