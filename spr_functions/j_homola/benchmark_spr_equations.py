#%%

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
import os

from scipy import constants
c     = constants.speed_of_light
mu_0  = constants.mu_0
eps_0 = constants.epsilon_0


PI = np.pi
DEG = PI/180

# lam0 = 984e-9
lam0 = 800e-9
f0   = c/lam0
# lam0 = np.arange(300e-9, 1000e-9, 1e-9)

k0   = 2*PI/lam0
omega0 = 2*PI*f0
eps_m = -25 + 1j*1.44
eps_d = 1.32**2

def beta_extended(eps_m, eps_d, k0):
    return k0*np.sqrt(np.real(eps_m)*eps_d/(np.real(eps_m) + eps_d)) + 1j*k0*(np.imag(eps_m)/(2*np.real(eps_m)**2))*(np.real(eps_m)*eps_d/(np.real(eps_m) + eps_d))**(3/2)

def beta(eps_m, eps_d, k0):
    return k0*np.sqrt(np.real(eps_m)*eps_d/(np.real(eps_m) + eps_d)) 

def gamma_m(k0, eps_m, eps_d):
    return -1j*k0*eps_m/np.sqrt(eps_m + eps_d, dtype=complex)

def gamma_d(k0, eps_m, eps_d):
    return 1j*k0*eps_d/np.sqrt(eps_m + eps_d, dtype=complex)

def h_y(x, eps_m, eps_d, k0):
    h_y = np.zeros(len(x), dtype=complex)
    for i in range(len(x)):
        if x[i] <= 0:
            h_y[i] = np.exp(gamma_m(k0, eps_m, eps_d)*x[i])
        else:
            h_y[i] = np.exp(-gamma_d(k0, eps_m, eps_d)*x[i])
    return h_y

def e_x(x, eps_m, eps_d, k0):
    e_x = np.zeros(len(x), dtype=complex)
    for i in range(len(x)):
        if x[i] <= 0:
            e_x[i] = (beta(eps_m, eps_d, k0)/(omega0*eps_m*eps_0))*np.exp(gamma_m(k0, eps_m, eps_d)*x[i])
        else:
            e_x[i] = (beta(eps_m, eps_d, k0)/(omega0*eps_d*eps_0))*np.exp(-gamma_d(k0, eps_m, eps_d)*x[i])
        
    return e_x

def e_z(x, eps_m, eps_d, k0):
    e_z = np.zeros(len(x), dtype=complex)
    for i in range(len(x)):
        if x[i] <= 0:
            e_z[i] = (beta(eps_m, eps_d, k0)/(omega0*eps_m*eps_0))*np.exp(gamma_m(k0, eps_m, eps_d)*x[i])
        else:
            e_z[i] = -(beta(eps_m, eps_d, k0)/(omega0*eps_d*eps_0))*np.exp(-gamma_d(k0, eps_m, eps_d)*x[i])
        
    return e_z


x = np.arange(-0.5e-6, 2e-6, 0.001e-6)

h_y_plot = h_y(x, eps_m, eps_d, k0)
h_y_norm = h_y_plot

e_x_plot = e_x(x, eps_m, eps_d, k0)
e_x_norm = e_x_plot

plt.figure(1)
plt.plot(x, np.real(h_y_norm))
plt.plot(x, np.real(h_y_norm)*2)
plt.plot(x, np.imag(h_y_norm))

#%%
plt.figure(2)
plt.plot(x, np.real(e_x_norm))
plt.plot(x, np.imag(e_x_norm))

#%%
plt.figure(3)
# plt.plot(x, np.real(e_z(x, eps_m, eps_d, k0)))
# plt.plot(x, np.imag(e_z(x, eps_m, eps_d, k0)))

#%%
lam0 = np.arange(600e-9, 1000e-9, 1e-9)
k0   = 2*PI/lam0
L_pm = 1/np.real(gamma_m(k0, eps_m, eps_d))

plt.figure(1)
plt.plot(lam0*1e9, L_pm*1e9)

#%%

lam0 = 984e-9
k0   = 2*PI/lam0
h    = np.arange(0, 100e-9, 10e-9)
n_d  = 1.33**2
delta_d = 0.3

# n_prism = 1.51, e_analyte = 1.33**2

def delta_n_eff(h, n_d, delta_d):
    return np.real(beta(eps_m, eps_d, k0)**3*(1 - np.exp(-2*gamma_d(k0, eps_m, eps_d)*h)))*delta_d/(k0**3*n_d**3)

# def delta_n_eff_delta_n(h):
#     return (np.real(eps_m)/(np.real(eps_m) + eps_d**2))**(3/2)*(2*eps_d**2/np.sqrt(-eps_m - eps_d**2))*h*k0

plt.figure(1)
plt.plot(h*1e9, delta_n_eff(h, n_d, delta_d))


def theta_SPR(h):
    return (np.sqrt((np.abs(eps_m)*(n_d + delta_n_eff(h, n_d, delta_d))**2)/(np.abs(eps_m) - (n_d + delta_n_eff(h, n_d, delta_d))**2)))

t_sub = 50e-9
x_SPR = 2*np.tan(np.arcsin(theta_SPR(h)))*t_sub

plt.figure(1)
plt.plot(h*1e9, x_SPR*1e6)