import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
import os

SPR_loc = lambda theta: 2*1.2*np.tan(np.pi/180 * theta)
SPR_ang = lambda dist: np.arctan(dist/(2*1.2))*180/np.pi
ref_idx = lambda x: x*1.474 + (1-x)*1.333

def load_SPR_data():
    filename = 'SPR_data'
    file_path = os.path.join('data', f'{filename}.txt')
    print(f"File path: {file_path}")  # Add this line for debugging
    df_full = pd.read_csv(file_path, delimiter='\t')
    df_full = df_full.sort_values(by=['w_glyc', 'theta'])
    return df_full

def get_SPR(glycerol_concentration):
    df_full = load_SPR_data()
    angs = df_full[df_full.w_glyc==glycerol_concentration].theta
    refs = df_full[df_full.w_glyc==glycerol_concentration].refl
    return angs, refs

def get_dips():
    df_full = load_SPR_data()
    
    dips_data = []    
    
    for conc in df_full.w_glyc.unique():
        refl_minimum = df_full[df_full.w_glyc==conc].refl.min()
        spr_theta = df_full[(df_full.w_glyc == conc) & (df_full.refl == refl_minimum)].theta.min()
        dips_data.append( [conc, ref_idx(conc), refl_minimum, spr_theta, SPR_loc(spr_theta)] )
        
    dips = pd.DataFrame(dips_data, columns=['Concentration', 'Ref Index', 'R', 'SPR Angle', 'Distance'])
    dips['Shift'] = dips['Distance'] - dips.loc[dips['Concentration'] == 0, 'Distance'].iloc[0]
    dips = dips[dips['Ref Index']<=1.34]
    return dips

def ResonantAngle(e_3r = -40.650+ 1j*2.2254, n_prism = 1.51, e_analyte = 1.33**2):
    param = np.sqrt((e_analyte * abs(e_3r)) / (abs(e_3r) - e_analyte)) / n_prism
    theta_spr = np.arcsin(param) * 180 / np.pi
    return theta_spr

def ResonantN(e_3r = -40.650+ 1j*2.2254, n_prism = 1.51, theta_spr = 64.5):
    param = np.sin(theta_spr*np.pi/180)
    e_analyte = (  abs(e_3r) * n_prism**2 * param**2  ) / (  abs(e_3r) + n_prism**2 * param**2  )
    return np.sqrt(e_analyte)

if __name__ == '__main__':
    #%% DATA IMPORT
    filename = 'SPR_data'
    df_full = pd.read_csv(f'data/{filename}.txt', delimiter='\t')
    df_full = df_full.sort_values(by=['w_glyc', 'theta'])
    
    
    
    #%% PLOT SAMPLE SPECTRUM
    glyc = 0.01
    sampling_rate = 0.1
    x_range = (63,66)
    
    fig = plt.figure(figsize = (15,7))
    
    ax1 = fig.add_subplot(121)
    ax1.scatter(df_full[df_full.w_glyc==0].theta, df_full[df_full.w_glyc==0].refl, label=f'Water n={ref_idx(0):.3f}')
    ax1.scatter(df_full[df_full.w_glyc==glyc].theta, df_full[df_full.w_glyc==glyc].refl, label=f'{glyc*100}% Glycerol n={ref_idx(glyc):.3f}')
    ax1.set_xlim(x_range)
    ax1.set_xticks(np.arange(x_range[0], x_range[1], 0.1))
    ax1.set_xticklabels(np.round(ax1.get_xticks(),1), rotation = 90)
    
    # ax1.set_ylim([0,0.2])
    ax1.set_xlabel('Angle, deg')
    ax1.set_ylabel('Reflectance')
    ax1.legend()
    ax1.grid(True, which='major', linestyle='--', linewidth=0.5, color='gray', alpha=0.7)
    
    ax2 = ax1.twiny()
    custom_tick_positions = np.arange(x_range[0], x_range[1], sampling_rate)
    custom_tick_labels = [round(SPR_loc(x), 3) for x in custom_tick_positions]  
    ax2.set_xlim(ax1.get_xlim())
    ax2.set_xticks(custom_tick_positions)
    ax2.set_xticklabels(custom_tick_labels, rotation=90)
    ax2.set_xlabel('Distance from VCSEL Source, mm')
    
    x_range = (64,65)
    ax1 = fig.add_subplot(122)
    ax1.scatter(df_full[df_full.w_glyc==0].theta, df_full[df_full.w_glyc==0].refl, label='Water')
    ax1.scatter(df_full[df_full.w_glyc==glyc].theta, df_full[df_full.w_glyc==glyc].refl, label=f'{glyc*100}% Glycerol')
    ax1.set_xlim(x_range)
    ax1.set_xticks(np.arange(x_range[0], x_range[1], 0.1))
    ax1.set_xticklabels(np.round(ax1.get_xticks(),1), rotation = 90)
    
    # ax1.set_ylim([0,0.2])
    ax1.set_xlabel('Angle, deg')
    ax1.set_ylabel('Reflectance')
    ax1.legend()
    ax1.grid(True, which='major', linestyle='--', linewidth=0.5, color='gray', alpha=0.7)
    
    ax2 = ax1.twiny()
    custom_tick_positions = np.arange(x_range[0], x_range[1], sampling_rate)
    custom_tick_labels = [round(SPR_loc(x), 3) for x in custom_tick_positions]  
    ax2.set_xlim(ax1.get_xlim())
    ax2.set_xticks(custom_tick_positions)
    ax2.set_xticklabels(custom_tick_labels, rotation=90)
    ax2.set_xlabel('Distance from VCSEL Source, mm')
    
    
    #%% FIND MINIMA
    dips_data = []
    
    
    for conc in df_full.w_glyc.unique():
        refl_minimum = df_full[df_full.w_glyc==conc].refl.min()
        spr_theta = df_full[(df_full.w_glyc == conc) & (df_full.refl == refl_minimum)].theta.min()
        dips_data.append( [conc, ref_idx(conc), refl_minimum, spr_theta, SPR_loc(spr_theta)] )
        
    dips = pd.DataFrame(dips_data, columns=['Concentration', 'Ref Index', 'R', 'SPR Angle', 'Distance'])
    dips['Shift'] = dips['Distance'] - dips.loc[dips['Concentration'] == 0, 'Distance'].iloc[0]
    dips = dips[dips['Ref Index']<=1.335]
        
    #%% PLOT
    
    fig = plt.figure(figsize = (10,7))
    # plt.subplots_adjust(wspace=0.5)
    
    ax1 = fig.add_subplot(231)
    ax1.scatter(dips['Concentration'], dips['SPR Angle'])
    ax1.set_xlabel('Glycerol Concentration')
    ax1.set_ylabel('SPR Angle')
    
    ax2 = fig.add_subplot(232)
    ax2.scatter(dips['Ref Index'], dips['SPR Angle'])
    ax2.set_xlabel('Refractive Index')
    ax2.set_ylabel('SPR Angle')
    
    
    ax3 = fig.add_subplot(233)
    ax3.scatter(dips['Ref Index'], dips['Distance'])
    ax3.set_xlabel('Refractive Index')
    ax3.set_ylabel('Distance')
    
    ax4 = fig.add_subplot(234)
    ax4.scatter(dips['Ref Index'], dips['Shift']*1000)
    ax4.set_xlabel('Refractive Index')
    # ax4.set_xticks(np.arange(1.33,1.34,0.001))
    # ax4.set_yticks(np.arange(0,200,20))
    ax4.set_ylabel('Shift')
    
    
    
    an_shift = lambda x: -29.73401 + 22.30604*x
    ref_indx = np.arange(1.333,1.335,1E-6)
    shifts = an_shift(ref_indx)
    
    analytical = pd.DataFrame(zip(ref_indx, shifts*1000), columns=['Ref index','Shift'])
    
    ax5 = fig.add_subplot(235)
    ax5.plot(analytical['Ref index'], analytical['Shift'])
    ax5.set_xlabel('Ref index')
    ax5.set_ylabel('Shift, um')
    
    
    
    
    
    
