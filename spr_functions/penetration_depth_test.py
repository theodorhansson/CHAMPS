#%%
import numpy as np
import matplotlib.pyplot as plt

PI=np.pi
eps1 = -40.650+ 1j*2.2254
eps2 = 1.33**2
wl = 984

# skin depth at spr in medium eps2
# ld_eps2 = wl/(2*PI) * np.sqrt( (abs(eps1) - eps2) / (eps2**2))

def ld(wl, theta, n_sub, n_analyte):
    ld = wl/ (2*np.pi*np.sqrt(n_sub**2*np.sin(theta)**2-n_analyte**2))
    return ld

def ResonantAngle(e_3r = -40.650+ 1j*2.2254, n_prism = 1.51, e_analyte = 1.33**2):
    param = np.sqrt((e_analyte * abs(e_3r)) / (abs(e_3r) - e_analyte)) / n_prism
    theta_spr = np.arcsin(param) * 180 / np.pi
    return theta_spr

ri = np.linspace(1.33, 1.45, 20)
ldep = np.zeros_like(ri)

for i, rii in enumerate(ri):
    ldep[i] = ld(984, ResonantAngle(e_analyte = rii**2)*PI/180, 1.51, rii)


plt.scatter(ri, ldep)

#%%

beta_sp = 2*PI/wl * np.sqrt((eps2*eps1)/(eps2+eps1))

sintet = np.real(beta_sp)*wl/2/PI/(1.51**2)
print(np.arcsin(sintet)*180/PI) 