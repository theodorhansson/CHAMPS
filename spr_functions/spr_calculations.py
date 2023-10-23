import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
import os

PI = np.pi
DEG = PI/180
theta = np.arange(0,90,0.1)*DEG

glass_thickness=1.05
SPR_loc = lambda theta: 2*glass_thickness*np.tan(np.pi/180 * theta)
SPR_ang = lambda dist: np.arctan(dist/(2*glass_thickness))*180/np.pi
ref_idx = lambda x: x*1.474 + (1-x)*1.33
# this is the length that ***intensity*** changes by 1/e
ld = lambda wl, theta: wl/ (4*np.pi*np.sqrt(1.51**2*np.sin(theta)**2-1.33**2))

# this is the length that ***field*** changes by 1/e
ld = lambda wl, theta: wl/ (2*np.pi*np.sqrt(1.51**2*np.sin(theta)**2-1.33**2))

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
#%%
if __name__ == '__main__':
    
    #%% DATA IMPORT
    filename = 'SPR_data'
    df_full = pd.read_csv(f'data/{filename}.txt', delimiter='\t')
    df_full = df_full.sort_values(by=['w_glyc', 'theta'])
    
    
    
    #%% PLOT SAMPLE SPECTRUM
    glyc = 0.01
    sampling_rate = 0.2
    x_range = (63,66)
    
    fig = plt.figure(figsize = (15,10))
    
    ax1 = fig.add_subplot(231)
    ax1.plot(df_full[df_full.w_glyc==0].theta, df_full[df_full.w_glyc==0].refl, label=f'Water n={ref_idx(0):.3f}')
    ax1.plot(df_full[df_full.w_glyc==glyc].theta, df_full[df_full.w_glyc==glyc].refl, label=f'{glyc*100}% Glycerol n={ref_idx(glyc):.3f}')
    ax1.set_xlim(x_range)
    ax1.set_xticks(np.arange(x_range[0], x_range[1]+sampling_rate, sampling_rate))
    ax1.set_xticklabels(np.round(ax1.get_xticks(),1), rotation = 90)
    
    # ax1.set_ylim([0,0.2])
    ax1.set_xlabel('Angle of Incidence, deg')
    ax1.set_ylabel('Reflectance')
    ax1.legend()
    # ax1.grid(True, which='major', linestyle='--', linewidth=0.5, color='gray', alpha=0.7)
    
    ax2 = ax1.twiny()
    custom_tick_positions = ax1.get_xticks()
    custom_tick_labels = [round(SPR_loc(x), 3) for x in custom_tick_positions]  
    ax2.set_xlim(ax1.get_xlim())
    ax2.set_xticks(custom_tick_positions)
    ax2.set_xticklabels(custom_tick_labels, rotation=90)
    ax2.set_xlabel('Distance from VCSEL Source, mm')
    
    x_range = (64,65)
    sampling_rate = 0.1
    ax3 = fig.add_subplot(232)
    ax3.plot(df_full[df_full.w_glyc==0].theta, df_full[df_full.w_glyc==0].refl, label='Water')
    ax3.plot(df_full[df_full.w_glyc==glyc].theta, df_full[df_full.w_glyc==glyc].refl, label=f'{glyc*100}% Glycerol')
    ax3.set_xlim(x_range)
    ax3.set_xticks(np.arange(x_range[0], x_range[1]+sampling_rate, sampling_rate))
    # ax1.set_xticklabels(np.round(ax1.get_xticks(),1), rotation = 90)
    
    # ax1.set_ylim([0,0.2])
    ax3.set_xlabel('Angle of Incidence, deg')
    ax3.set_ylabel('Reflectance')
    ax3.legend()
    # ax1.grid(True, which='major', linestyle='--', linewidth=0.5, color='gray', alpha=0.7)
    
    ax4 = ax3.twiny()
    custom_tick_positions = ax3.get_xticks()
    custom_tick_labels = [round(SPR_loc(x), 3) for x in custom_tick_positions]  
    ax4.set_xlim(ax3.get_xlim())
    ax4.set_xticks(custom_tick_positions)
    ax4.set_xticklabels(custom_tick_labels, rotation=90)
    ax4.set_xlabel('Distance from VCSEL Source, mm')
    
    # plt.show()
    
    # #%% FIND MINIMA
    # dips_data = []
    
    
    # for conc in df_full.w_glyc.unique():
    #     refl_minimum = df_full[df_full.w_glyc==conc].refl.min()
    #     spr_theta = df_full[(df_full.w_glyc == conc) & (df_full.refl == refl_minimum)].theta.min()
    #     dips_data.append( [conc, ref_idx(conc), refl_minimum, spr_theta, SPR_loc(spr_theta)] )
        
    # dips = pd.DataFrame(dips_data, columns=['Concentration', 'Ref Index', 'R', 'SPR Angle', 'Distance'])
    # dips['Shift'] = dips['Distance'] - dips.loc[dips['Concentration'] == 0, 'Distance'].iloc[0]
    # dips = dips[dips['Ref Index']<=1.335]
        
    # #%% PLOT
    
    # fig = plt.figure(figsize = (10,7))
    # # plt.subplots_adjust(wspace=0.5)
    
    # ax1 = fig.add_subplot(231)
    # ax1.scatter(dips['Concentration'], dips['SPR Angle'])
    # ax1.set_xlabel('Glycerol Concentration')
    # ax1.set_ylabel('SPR Angle')
    
    # ax2 = fig.add_subplot(232)
    # ax2.scatter(dips['Ref Index'], dips['SPR Angle'])
    # ax2.set_xlabel('Refractive Index')
    # ax2.set_ylabel('SPR Angle')
    
    
    # ax3 = fig.add_subplot(233)
    # ax3.scatter(dips['Ref Index'], dips['Distance'])
    # ax3.set_xlabel('Refractive Index')
    # ax3.set_ylabel('Distance')
    
    # ax4 = fig.add_subplot(234)
    # ax4.scatter(dips['Ref Index'], dips['Shift']*1000)
    # ax4.set_xlabel('Refractive Index')
    # # ax4.set_xticks(np.arange(1.33,1.34,0.001))
    # # ax4.set_yticks(np.arange(0,200,20))
    # ax4.set_ylabel('Shift')
    
    
    
    # an_shift = lambda x: -29.73401 + 22.30604*x
    # ref_indx = np.arange(1.333,1.335,1E-6)
    # shifts = an_shift(ref_indx)
    
    # analytical = pd.DataFrame(zip(ref_indx, shifts*1000), columns=['Ref index','Shift'])
    
    # ax5 = fig.add_subplot(235)
    # ax5.plot(analytical['Ref index'], analytical['Shift'])
    # ax5.set_xlabel('Ref index')
    # ax5.set_ylabel('Shift, um')
    
     

   
    

    sprx = [SPR_loc(th/DEG)*1000-SPR_loc(64.4)*1000 for th in theta]

    ax5 = fig.add_subplot(233)
    ax5.plot(theta*180/np.pi, sprx, label='Flat Biosensor')
    ax5.set_xlim([64.4,65.4])
    ax5.set_ylim([-50,300])
    ax5.set_xlabel('SPR Angle, deg')
    ax5.set_ylabel('SPR Coordinate on Detector, um')


    ax6 = ax5.twiny()
    ax6.set_xlim(ax5.get_xlim())
    ax6.set_xticklabels([np.round(ResonantN(theta_spr = th),3) for th in ax5.get_xticks()], rotation=90)
    ax6.set_xlabel('Refractive Index')


    theta_p = 70*DEG
    L = 10000
    x0 = 1710

    SPR_loc_prism = lambda theta_SPR, theta_p, x0, L: L / (np.cos(theta_p) + np.sin(theta_p)*np.tan(theta_SPR)) - x0

    x_water = SPR_loc_prism(64.4*np.pi/180, theta_p, x0, L)
    spr_prism_x = [-SPR_loc_prism(th, theta_p, x0, L)+x_water for th in theta]

    ax5.plot(theta*180/np.pi, spr_prism_x, label='Prism Biosensor')

    ldeps = [ld(984, th) for th in theta]
    ax7 = ax5.twinx()
    ax7.plot(theta*180/np.pi, ldeps, label = '984 nm', c='g', linestyle='--')
    ax7.set_ylim([440,560])
    ax7.set_ylabel('Field Penetration Depth, nm')
    ax5.legend(loc='upper left')
    ax7.legend()
    
    S = 18945 #um/RIU
    ns = 1.45
    nw = 1.33
    d = 5 #nm
    m = np.arange(10)+1
    dx = np.zeros_like(m, dtype=float)
    neff = np.zeros_like(m, dtype=float)
    ax8 = fig.add_subplot(234)
    ldep = ld(984, 64.4*DEG)
    
    thet = ResonantAngle(e_analyte=nw**2)
    ldep = ld(984, thet*DEG)
    
    for i, mm in  enumerate(m):  
        dx[i] = S * (ns-nw) * (1 - np.exp(-2*d*(mm-1)/ldep))
        neff[i] = nw + (ns-nw) * (1 - np.exp(-2*d*(mm-1)/ldep))
        thet = ResonantAngle(e_analyte=neff[i]**2)
        ldep = ld(984, thet*DEG)
    
    # dx = S * (ns-nw) * (1 - np.exp(-2*d*(m-1)/ldep))
    ax8.scatter(m,dx, edgecolor='b',facecolor='none')    
    # ax8.set_xlim((m*d)[0], (m*d)[-1])
    # ax8.set_xticks(m)    
    ax8.set_xlabel('Layer No')
    ax8.set_ylabel('SPR Coordinate on Detector, um')
    
    plt.tight_layout()
    # fig.savefig('figure.eps', dpi=300)
    # plt.show()

    refractive_index = np.arange(1.33, 1.340, 0.000001)
    resonant_angles = [ResonantAngle(e_analyte=n**2) for n in refractive_index]
    detector_positions = [(SPR_loc(th)-SPR_loc(ResonantAngle(e_analyte=1.33**2)))*1000 for th in resonant_angles]
    ax9 = fig.add_subplot(235)
    ax9.scatter(refractive_index, detector_positions, s=1, label='position on detector')
    
    coefficients = np.polyfit(refractive_index[0:10], detector_positions[0:10], 1)
    
    y = refractive_index*coefficients[0] + coefficients[1]
    ax9.plot(refractive_index,y, c='r', label='linear fit')
    ax9.legend()
    print(coefficients)
    
    dy_dx = np.gradient(detector_positions, refractive_index)
    
    ax10 = fig.add_subplot(236)
    ax10.plot(refractive_index, dy_dx, label='sensitivity')
    ax10.legend()
    # plt.show()
    # plt.scatter(resonant_angles, detector_positions, s=1)
    
    # plt.plot(refractive_index, resonant_angles)
    # plt.show()
    # plt.plot(refractive_index, np.gradient(resonant_angles,refractive_index))
    
