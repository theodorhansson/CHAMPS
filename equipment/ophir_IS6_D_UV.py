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
_optional_arguments = {"verbose_printing": 0}


class INT_sphere:
    def __init__(self, config_dict: dict):
        utils.argument_checker(
            config_dict, _required_arguments, _optional_arguments, source_func="sphere"
        )
        config_dict = utils.optional_arguments_merge(config_dict, _optional_arguments)

        self._min_time = config_dict["min_measure_time"]
        self.range = config_dict["range"]
        self.wavelength = config_dict["wavelength"]
        self.verbose = config_dict["verbose_printing"]

        print("__init__() in IS6-D-UV") if self.verbose & 4 + 8 else None

    def __enter__(self):
        print("__enter__() in IS6-D-UV") if self.verbose & 8 else None

        self.open()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if self.verbose & 8:
            print("__exit__() in IS6-D-UV")
            print(f"{exception_type=}, {exception_value=}, {exception_traceback=}")

        self.close()

    def open(self):
        print("open() in IS6-D-UV") if self.verbose & 8 else None

        self._OphirCOM = win32com.client.Dispatch("OphirLMMeasurement.CoLMMeasurement")
        device_list = self._OphirCOM.ScanUSB()
        try:
            device = device_list[0]
        except:
            # print("You don't seem to have an Integrating Sphere connected")
            raise ConnectionError("Integrating Sphere connection failed.")
        self._device_handle = self._OphirCOM.OpenUSBDevice(device)

        # Set the default range
        self.set_range(self.range)
        # Set sensivitve wavelength
        self.set_wavelength(self.wavelength)
        # Start output stream
        self.set_output(True)

    def close(self):
        # Stops and disconnects all OphirCOM
        print("close() in IS6-D-UV") if self.verbose & 8 else None

        self._OphirCOM.StopAllStreams()
        self._OphirCOM.CloseAll()

    def set_min_time(self, min_time: float):
        # If you want to change min_time later
        if self.verbose & 8:
            print(f"set_min_time() in sphere: setting to {min_time}")

        self._min_time = min_time

    def get_power(self):
        # Get reading from int. sphere

        time.sleep(self._min_time)
        data = self._OphirCOM.GetData(self._device_handle, 0)
        # Checks if there is any data
        if len(data[0]) > 0:
            # Extract last power value from datastream
            power = data[0][-1]
            power = power * 1e3  # W to mW
        else:
            # print("Not connected/initialized")
            # print("Get_power_none", data)
            power = None  # TODO Decide what value should be here

        if self.verbose & 8:
            print(f"get_power() in IS6-D-UV: value {power}")
        return power

    def set_range(self, new_range: int):
        # Set the measurement-range for the sphere
        if self.verbose & 8:
            print(f"set_range() in IS6-D-UV: setting to {new_range}")

        accepted_ranges = [0, 1, 2, 3, 4, 5, 6, 7]
        new_range = utils.closest_matcher(
            new_range, accepted_ranges, round_type="exact", msg="IS6-D-UV ranges"
        )

        self._OphirCOM.SetRange(self._device_handle, 0, int(new_range))

    def get_ranges(self):
        # Return the possible ranges
        ranges = self._OphirCOM.GetRanges(self._device_handle, 0)

        if self.verbose & 8:
            print(f"get_ranges() in IS6-D-UV: value {ranges}")
        return ranges

    def get_wavelengths(self):
        # Returns possible ranges
        # ((current index),('940', '300',...))
        wavelengths = self._OphirCOM.GetWavelengths(self._device_handle, 0)

        if self.verbose & 8:
            print(f"get_wavelengths() in IS6-D-UV: value {wavelengths}")
        return wavelengths

    def set_wavelength(self, new_wave_length: int):
        # Set the wavelength calibration
        if self.verbose & 8:
            print(f"set_wavelength() in IS6-D-UV: setting to {new_wave_length}")

        accepted_wl = [0, 1, 2, 3, 4, 5]
        new_wave_length = utils.closest_matcher(
            new_wave_length, accepted_wl, round_type="exact", msg="IS6-D-UV wavelength"
        )

        self._OphirCOM.SetWavelength(self._device_handle, 0, int(new_wave_length))

    def set_output(self, state: bool):
        # Toggles reading from sphere

        if self.verbose & 4 + 8:
            if state:
                print("set_output() in IS6-D-UV: Enabling")
            else:
                print("set_output() in IS6-D-UV: Disabling")

        if state:
            self._OphirCOM.StartStream(self._device_handle, 0)
            # Wait for instrument to start
            for _ in range(10):
                data = self.get_power()
                # print(data)
                if data != None:
                    break
                else:
                    # Wait for start
                    time.sleep(0.4)
        else:
            self._OphirCOM.StopStream(self._device_handle, 0)

    def get_device_list(self):
        # Get list of connected devices
        devices = self._OphirCOM.ScanUSB()

        if self.verbose & 8:
            print(f"get_device_list() in IS6-D-UV: devices {devices}")
        return devices

    def get_device_handle(self):
        # Get name of current device_handle

        device_handle = self._device_handle
        if self.verbose & 8:
            print(f"get_device_handle() in IS6-D-UV: devices {device_handle}")
        return device_handle


def test(sphere_obj):
    sphere_obj._OphirCOM.StartStream(sphere_obj._DeviceHandle, 0)
    for _ in range(10):
        time.sleep(0.2)  # wait a little for data
        data = sphere_obj._OphirCOM.GetData(sphere_obj._DeviceHandle, 0)
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
