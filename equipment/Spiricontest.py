import os, sys, clr, time
import pythonnet
import matplotlib.pyplot as plt

clr.AddReference("..\\beamgage_drivers\\Beamgage_python_wrapper")
import Beamgage_python_wrapper

_bg = Beamgage_python_wrapper.Beamgage("FROM_PYTH", True)
bg = _bg.get_AutomatedBeamGage()


res = bg.ResultsPriorityFrame.DoubleData
print(dir(bg))
print(res)
time.sleep(10)
bg.Instance.Shutdown()
