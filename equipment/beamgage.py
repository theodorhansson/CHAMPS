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
        self.close()

    def close(self):
        print("close() in Beamgage") if self.verbose & 8 else None
        self.bg.Instance.Shutdown()

    def get_frame_data(self) -> list:
        print("get_frame_data() in Beamgage") if self.verbose & 8 else None

        data_NET = self.bg.ResultsPriorityFrame.DoubleData

        # If data_NET is something (not None) all good, else raise Exception
        for i in range(15):
            if self.get_frame_data():
                break
            time.sleep(1)
        else:
            raise Exception("Beamgage camera didn't respond. Is it connected?")

        shape = self.get_frame_shape()
        matrix = np.array(data_NET)
        matrix = np.reshape(matrix, shape)
        return list(matrix)

    def get_frame_shape(self) -> tuple[int, int]:
        print("get_frame_shape() in Beamgage") if self.verbose & 8 else None

        width = int(self.bg.get_FrameInfoResults().Width)
        height = int(self.bg.get_FrameInfoResults().Height)
        return (height, width)

    def calibrate(self):
        print("calibrate() in Beamgage") if self.verbose & 8 else None
        self.bg.Calibration.Ultracal()
