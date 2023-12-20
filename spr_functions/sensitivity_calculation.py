#%%
import numpy as np
import matplotlib.pyplot as plt

### SENSITIVITY AS A FUNCTION OF THICKNESS

x = lambda theta, t: 2*t*np.tan(theta)

def ResonantAngle(e_3r = -40.650+ 1j*2.2254, n_prism = 1.51, e_analyte = 1.33**2):
    param = np.sqrt((e_analyte * abs(e_3r)) / (abs(e_3r) - e_analyte)) / n_prism
    theta_spr = np.arcsin(param) * 180 / np.pi
    return theta_spr

ts = [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]

ns = np.arange(1.33, 1.40, 0.00001)
angles = np.array([ResonantAngle(e_analyte = n**2) for n in ns])

xs = {}
dxs_dns = {}

fig, axs = plt.subplots(1,2)

for t in ts:
    xs[t] = [x(angle*np.pi/180, t) for angle in angles] 
    dxs_dns[t] = np.gradient(xs[t], ns)
    axs[0].plot(ns, xs[t], label=f'Thickness {t}')
    axs[1].plot(ns, dxs_dns[t], label=f'Thickness {t}')

axs[0].legend(fontsize=5)
axs[0].set_title('Detector Position, mm')
axs[1].legend(fontsize=5)
axs[1].set_title('Sensitivity, mm/RIU')
plt.tight_layout()

#%%

ts = [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]

ns = np.arange(1.33, 1.40, 0.00001)
angles = np.array([ResonantAngle(e_analyte = n**2) for n in ns])

xs = {}
dxs_dns = {}

fig, axs = plt.subplots(1,1)

for t in ts:
    xs[t] = [x(angle*np.pi/180, t) for angle in angles] 
    # dxs_dns[t] = np.gradient(xs[t], ns)
    axs.plot(ns, xs[t], label=f'Thickness {t}')
    # axs[1].plot(ns, dxs_dns[t], label=f'Thickness {t}')

axs.legend(fontsize=5)
axs.set_title('Detector Position, mm')
# axs[1].legend(fontsize=5)
# axs[1].set_title('Sensitivity, mm/RIU')
plt.tight_layout()

