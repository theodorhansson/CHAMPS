import win32com.client
import time
import traceback

# Idé: Få upp ett GUI om fler än en ophir ansluten samtidigt
# OBS: bör nog lägga in en fördröjning mellan mätningar. Hantera i IPV?
# TODO testa mig på sfär

# Based on python example from Ophir

_required_arguments = [
    "range",
]


class INT_sphere:
    def __init__(self, config_dict):
        self._OphirCOM = win32com.client.Dispatch("OphirLMMeasurement.CoLMMeasurement")
        DeviceList = self._OphirCOM.ScanUSB()
        Device = DeviceList[0]
        self._DeviceHandle = self._OphirCOM.OpenUSBDevice(Device)

        # Set the default range
        default_range = config_dict["range"]
        self._OphirCOM.SetRange(self._DeviceHandle, 0, default_range)

        # exists = OphirCOM.IsSensorExists(self._DeviceHandle, 0)
        # if exists:

    def get_power(self):
        # Get reading from int. sphere
        data = self._OphirCOM.GetData(self._DeviceHandle, 0)
        power = data[0][0]
        return power

    def set_range(self, newRange):
        # Set the measurement-range for the sphere
        self._OphirCOM.SetRange(self._DeviceHandle, 0, newRange)

    def get_ranges(self):
        # Return the possible ranges
        ranges = self._OphirCOM.GetRanges(self._DeviceHandle, 0)
        return ranges

    def set_output(self, state):
        # Toggles reading from sphere
        if state:
            self._OphirCOM.StartStream(self._DeviceHandle, 0)
        else:
            self._OphirCOM.StopStream(self._DeviceHandle, 0)

    def get_device_list(self):
        # Get list of connected devices
        return self._OphirCOM.ScanUSB()

    def get_device_handle(self):
        # Get name of current device_handle
        return self._DeviceHandle

    def __del__(self):
        # Stops and disconnects OphirCOM
        self._OphirCOM.StopAllStreams()
        self._OphirCOM.CloseAll()


def sphere_tests():
    pass


if __name__ == "__main__":
    sphere_tests()
