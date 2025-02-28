import numpy as np
import matplotlib.pyplot as plt

### SENSITIVITY AS A FUNCTION OF THICKNESS

x = lambda theta, t: 2*t*np.tan(theta)
x_th = lambda x, t: np.arctan(x/2/t)

def ResonantAngle(e_3r = -40.650+ 1j*2.2254, n_prism = 1.51, e_analyte = 1.33**2):
    param = np.sqrt((e_analyte * abs(e_3r)) / (abs(e_3r) - e_analyte)) / n_prism
    theta_spr = np.arcsin(param) * 180 / np.pi
    return theta_spr

fig, axs = plt.subplots(1,3, figsize=(8,3))

# ts = [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]
ts=[1.2, 1.4, 1.6]
ps=[26, 31, 36]

ns = np.arange(1.33, 1.38, 0.00001)
angles = np.array([ResonantAngle(e_analyte = n**2) for n in ns])

PI=np.pi
DEG = PI/180

# plot coordinate on a hypothetical prism sensors versus angle
theta_p = 70*DEG
# L = 30
H = 10
x0 = H/np.sin(theta_p)

SPR_loc_prism = lambda theta_SPR, theta_p, L: L* np.sin(90*DEG - theta_SPR)/(2*np.sin(90*DEG - theta_p + theta_SPR))

spr_prism_x = {}
spr_prism_dx_dn = {}

for L in ps:
    spr_prism_x[L] = np.array([x0-SPR_loc_prism(th*DEG, theta_p, L) for th in angles])
    spr_prism_dx_dn[L] = np.gradient(spr_prism_x[L], ns)

    axs[2].plot(ns, spr_prism_x[L]-min(spr_prism_x[L]), '--', label=f'Prism of {L}x{H} mm size')
    axs[1].plot(ns, spr_prism_dx_dn[L],'--', label=f'Prism of {L}x{H} mm size')

xs = {}
dxs_dns = {}



for t in ts:
    xs[t] = np.array([x(angle*np.pi/180, t) for angle in angles])
    dxs_dns[t] = np.gradient(xs[t], ns)
    axs[2].plot(ns, xs[t]-min(xs[t]), label=f'Thickness {t}')
    axs[1].plot(ns, dxs_dns[t], label=f'Thickness {t}')

axs[2].set_title('Sensor Readout')
axs[2].set_xlabel('Refractive index')
axs[2].set_ylabel('x on detector, [mm]')
axs[1].set_title('Device SPR Sensitivity')
axs[1].set_xlabel('Refractive index')
axs[1].set_ylabel('dx / dn, [mm/RIU]')

axs[1].legend(fontsize=5)
axs[2].legend(fontsize=5)

dth_dn = np.gradient(angles, ns)
axs[0].plot(ns, dth_dn)
axs[0].set_xlabel('Refractive index')
axs[0].set_ylabel('dtheta / dn, [angle/RIU]')
axs[0].set_title('Deviceless SPR Sensitivity')

plt.tight_layout()