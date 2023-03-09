import os, sys, clr, time
import pythonnet
import matplotlib.pyplot as plt

clr.AddReference("..\\beamgage_drivers\\Beamgage_python_wrapper")
import Beamgage_python_wrapper

bg_class = Beamgage_python_wrapper.Beamgage("FROM_PYTH", True)
bg = bg_class.get_AutomatedBeamGage()


res = bg_class.get_Data_Double()
res_str = bg_class.get_Data_string()

res = [x for x in res]

print(dir(bg))
print(len(res))
print(res_str)
time.sleep(10)
bg.Instance.Shutdown()
