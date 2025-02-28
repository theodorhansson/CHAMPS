#%%

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

def exp_func(x, a, b, c):
    return a * np.exp(b * x) + c

miRNA_c    = np.array([20,  20,  5,   1,   1,  0.5, 0.1, 0.1, 0.05, 0.02, 0.01])
miRNA_r    = np.array([120, 116, 24,  7.6, 5,  4,   1.2, 1.4, 0.7,  0.3,  0.1])
anitbody_r = np.array([600, 580, 120, 38,  25, 20,  6,   7,   3.5,  1.5,  0.5])

conc = np.linspace(miRNA_c.min(), miRNA_c.max(), 1000)

popt, pcov = curve_fit(exp_func, miRNA_c, miRNA_r)
plt.plot(conc, exp_func(conc, *popt), 'r-', label="Fitted Curve")
plt.plot(miRNA_c, miRNA_r, 'x')


#%%
plt.plot(np.log10(conc), exp_func(conc, *popt), color='black')
plt.plot(np.log10(miRNA_c), miRNA_r, 'rx')


#%%

popt, pcov = curve_fit(exp_func, miRNA_c, anitbody_r)
plt.plot(np.log10(conc), exp_func(conc, *popt), color='black')
plt.plot(np.log10(miRNA_c), anitbody_r, 'rx')