import os, sys, clr, time
import pythonnet
import matplotlib.pyplot as plt
import numpy as np

clr.AddReference("..\\drivers\\beamgage_drivers\\Beamgage_python_wrapper")
import Beamgage_python_wrapper

bg_class = Beamgage_python_wrapper.Beamgage("FROM_PYTH", True)
bg = bg_class.get_AutomatedBeamGage()


res = bg.ResultsPriorityFrame.DoubleData
res = [x for x in res]
print("len  ", len(res), "\tmax  ", np.max(res))

print("Getting frame info:")
width = int(bg.get_FrameInfoResults().Width)
height = int(bg.get_FrameInfoResults().Height)

res_arr = np.array[res]
matrix = np.reshape(res_arr, (height, width))
plt.imshow(matrix)
plt.show()
time.sleep(1)
# bg.Instance.Shutdown()
