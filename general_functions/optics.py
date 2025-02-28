#%%

import numpy as np

## Numerical aperture
PI = np.pi

#%%
what_angle = 20
n = 1
NA = n*np.sin(what_angle*PI/180)

print(str(round(what_angle, 2)) + ' degrees -> NA = ' + str(NA) + ' for n = ' + str(round(n, 2)))

#%%
what_NA = 0.34
n = 1
angle = np.arcsin(what_NA/n)*180/PI

print(str(round(what_NA, 2)) + ' NA -> theta = ' + str(round(angle, 2)) + ' for n = ' + str(round(n, 2)))
