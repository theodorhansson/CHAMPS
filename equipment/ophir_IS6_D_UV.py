import win32com.client
import time
import utils

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

# Avaliable wavelengths for IS6-D-UV
# 0    940 nm
# 1    300 nm
# 2    633 nm
# 3    543 nm
# 4    870 nm
# 5    850 nm


_required_arguments = ["range", "min_measure_time", "wavelength", "type"]


class INT_sphere:
    def __init__(self, config_dict: dict):
        utils.argument_checker(config_dict, _required_arguments, source_func="sphere")
        self._OphirCOM = win32com.client.Dispatch("OphirLMMeasurement.CoLMMeasurement")
        DeviceList = self._OphirCOM.ScanUSB()
        try:
            Device = DeviceList[0]
        except Exception as e:
            print("You don't seem to have an Integrating Sphere connected")
            raise e
        self._DeviceHandle = self._OphirCOM.OpenUSBDevice(Device)
        self._min_time = config_dict["min_measure_time"]

        # Set the default range
        default_range = config_dict["range"]
        self.set_range(default_range)

        # Set sensivitve wavelength
        wavelength = config_dict["wavelength"]
        self.set_wavelength(wavelength)

    def open(self):
        # Start output stream
        self.set_output(True)

    def set_min_time(self, min_time: float):
        # If you want to change min_time later
        self._min_time = min_time

    def get_power(self):
        # Get reading from int. sphere
        time.sleep(self._min_time)
        data = self._OphirCOM.GetData(self._DeviceHandle, 0)
        # Checks if there is any data
        if len(data[0]) > 0:
            # Extract last power value from datastream
            power = data[0][-1]
            power = power * 1e3  # W to mW
            return power
        else:
            # print("Not connected/initialized")
            print("Get_power_none", data)
            return None  # TODO Decide what value should be here

    def set_range(self, newRange: int):
        # Set the measurement-range for the sphere
        self._OphirCOM.SetRange(self._DeviceHandle, 0, int(newRange))

    def get_ranges(self):
        # Return the possible ranges
        ranges = self._OphirCOM.GetRanges(self._DeviceHandle, 0)
        return ranges

    def get_wavelengths(self):
        # Returns possible ranges
        # ((current index),('940', '300',...))
        wavelengths = self._OphirCOM.GetWavelengths(self._DeviceHandle, 0)
        return wavelengths

    def set_wavelength(self, newWavelength: int):
        self._OphirCOM.SetWavelength(self._DeviceHandle, 0, int(newWavelength))

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

    def close(self):
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
