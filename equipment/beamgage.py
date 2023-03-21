import clr
import numpy as np
import time
import sys, pathlib

root_folder = str(pathlib.Path(__file__).parent.parent.resolve())
# Dumb code to import utils
try:
    import utils
except:
    sys.path.append(root_folder)
    import utils  # Utils are placed in root folder of CHAMPS

_required_arguments = ["type"]
_optional_arguments = {
    "dll_path": root_folder + "\\drivers\\beamgage_drivers\\Beamgage_python_wrapper",
    "verbose_printing": 0,
    "keep_beamgage": 0,
}


class BeamCamera:
    def __init__(self, config_dict: dict):
        utils.argument_checker(
            config_dict,
            _required_arguments,
            _optional_arguments,
            source_func="Beam camera init",
        )
        config_dict = utils.optional_arguments_merge(config_dict, _optional_arguments)

        self.dll_path = config_dict["dll_path"]
        self.verbose = config_dict["verbose_printing"]
        self.keep_beamgage = config_dict["keep_beamgage"]
        print("__init__() in Beamgage") if self.verbose & 4 + 8 else None

    def open(self):
        clr.AddReference(self.dll_path)
        import Beamgage_python_wrapper

        # Gets the DLL wrapper class
        bg_class = Beamgage_python_wrapper.Beamgage("CHAMPS", True)

        # Gets the desired AutomatedBeamGage .NET obj
        self.bg = bg_class.get_AutomatedBeamGage()

    def __enter__(self):
        print("__enter__() in Beamgage") if self.verbose & 8 else None
        self.open()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if self.verbose & 8:
            print("__exit__() in Beamgage")
            print(f"{exception_type=}, {exception_value=}, {exception_traceback=}")
        if not self.keep_beamgage:
            self.close()

    def close(self):
        print("close() in Beamgage") if self.verbose & 8 else None
        self.bg.Instance.Shutdown()

    def _get_raw_frame_data(self) -> list:
        data_NET = self.bg.ResultsPriorityFrame.DoubleData
        data_pyth = [x for x in data_NET]
        return data_pyth

    def get_frame_data(self, retry=True) -> list:
        # Sleep to make sure the camera captures a pic of the newly set bias current
        time.sleep(0.25)

        for i in range(5):
            data_list = self._get_raw_frame_data()

            # If NOT none, break loop, else sleep and fetch again
            if data_list:
                break

            if self.verbose & 8:
                print("get_frame_data() in Beamgage: retrying data fetch ", i)
            time.sleep(1)
        else:
            raise Exception("Beamgage camera didn't respond. Is it connected?")

        shape = self.get_frame_shape()
        matrix = np.array(data_list)
        min = np.min(matrix)
        max = np.max(matrix)
        length = len(matrix)

        if length != (shape[0] * shape[1]):  # length = no of pixels = height * width
            if retry:  # Try once more to get a good picture, else except
                return self.get_frame_data(retry=False)
            else:
                raise Exception("The frame data didn't have the excpected shape.")

        matrix = np.reshape(matrix, shape)

        if self.verbose & 8:
            print(f"get_frame_data() in Beamgage: {length=} {shape=} {min=} {max=}")

        return [[int(element) for element in row] for row in matrix]

    def get_frame_shape(self) -> tuple[int, int]:
        width = int(self.bg.get_FrameInfoResults().Width)
        height = int(self.bg.get_FrameInfoResults().Height)
        ans = (height, width)
        if self.verbose & 8:
            print(f"shape() in Beamgage: value {ans}")
        return ans

    def calibrate(self):
        # This isn't optimal. Better to do it in the BeamGage GUI.
        print("calibrate() in Beamgage") if self.verbose & 8 else None
        self.bg.Calibration.Ultracal()
