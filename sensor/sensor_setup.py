#%%

import numpy as np
import matplotlib.pyplot as plt

### Defiinitions
PI = np.pi
DEG_TO_RAD = PI/180
RAD_TO_DEG = 180/PI
theta = np.arange(0,90,0.1)*DEG_TO_RAD
MM = 1e-3
UM = 1e-6
NM = 1e-9

### Plot arguments
fontsize_title  = 18
fontsize_label  = 16
fontsize_ticks  = 14
figure_width    = 10
figure_height   = 8
fontsize_legend = 12


def plot_sensor_setup(glass_thickness,
                      water_theta_spr_rad, glycerol_theta_spr_rad,
                      n_low, n_high,
                      deflection_angle,
                      deflection_to, deflection_from):
    
    extent_sensor = np.array([-5000, 10000])*UM
    
    ### VCSEL chip
    vcsel_pos_first_row  = 300*UM
    vcsel_pos_second_row = -400*UM
    vcsel_pos_third_row  = -1100*UM
    vcsel_pos_x = np.array([vcsel_pos_first_row, vcsel_pos_second_row, vcsel_pos_third_row])
    chip_size = np.array([-2000, 2000])*UM
    
    vcsel_glass_interface_y = 0
    
    ### Sensor chip
    gold_sensor_x = np.array([0, 8000])*UM
    gold_sensor_y = np.array([-glass_thickness, -glass_thickness])
    
    ### Gold detection lines
    gold_lines_x = np.array([600, 14000])*UM
    gold_lines_y = np.array([vcsel_glass_interface_y, vcsel_glass_interface_y])
    
    
    ### Rays from lasers
    ## Which laser
    turn_on_row = 0
    
    ## Main lobe
    laser_pos_glass_x = vcsel_pos_x[turn_on_row]
    laser_pos_glass_y = vcsel_glass_interface_y
    laser_pos_Au_x    = vcsel_pos_x[turn_on_row] + glass_thickness*np.tan(deflection_angle)
    laser_pos_Au_y    = -glass_thickness
    laser_first_bounce_x = laser_pos_Au_x + glass_thickness*np.tan(deflection_angle)
    laser_first_bounce_y = vcsel_glass_interface_y
    
    ## Upper limit
    upper_limit_pos_Au_x    = vcsel_pos_x[turn_on_row] + glass_thickness*np.tan(deflection_to)
    upper_limit_pos_Au_y    = -glass_thickness
    upper_limit_first_bounce_x = laser_pos_Au_x + glass_thickness*np.tan(deflection_to)
    upper_limit_first_bounce_y = vcsel_glass_interface_y
    
    ## Lower limit
    lower_limit_pos_Au_x    = vcsel_pos_x[turn_on_row] + glass_thickness*np.tan(deflection_from)
    lower_limit_pos_Au_y    = -glass_thickness
    lower_limit_first_bounce_x = laser_pos_Au_x + glass_thickness*np.tan(deflection_from)
    lower_limit_first_bounce_y = vcsel_glass_interface_y
    
    ## Rays
    center_ray_x = np.array([laser_pos_glass_x, laser_pos_Au_x, laser_first_bounce_x])
    center_ray_y = np.array([laser_pos_glass_y, laser_pos_Au_y, laser_first_bounce_y])
    upper_ray_x = np.array([laser_pos_glass_x, upper_limit_pos_Au_x, upper_limit_first_bounce_x])
    upper_ray_y  = np.array([laser_pos_glass_y, upper_limit_pos_Au_y, upper_limit_first_bounce_y])
    lower_ray_x = np.array([laser_pos_glass_x, lower_limit_pos_Au_x, lower_limit_first_bounce_x])
    lower_ray_y  = np.array([laser_pos_glass_y, lower_limit_pos_Au_y, lower_limit_first_bounce_y])
    
    
    ## Water SPR dip
    water_spr_dip = vcsel_pos_x[turn_on_row] + glass_thickness*np.tan(water_theta_spr_rad)
    water_spr_x = np.array([water_spr_dip, water_spr_dip])
    water_spr_y = np.array([-glass_thickness, -glass_thickness + 0.1*MM])
    water_spr_dip_first_bounce = vcsel_pos_x[turn_on_row] + 2*glass_thickness*np.tan(water_theta_spr_rad)
    water_spr_first_bounce_x = np.array([water_spr_dip_first_bounce, water_spr_dip_first_bounce])
    water_spr_first_bounce_y = np.array([vcsel_glass_interface_y, vcsel_glass_interface_y - 0.1*MM])
    
    ## Glycerol DPR dip
    glycerol_spr_dip = vcsel_pos_x[turn_on_row] + glass_thickness*np.tan(glycerol_theta_spr_rad)
    glycerol_spr_x = np.array([glycerol_spr_dip, glycerol_spr_dip])
    glycerol_spr_y = np.array([-glass_thickness, -glass_thickness + 0.1*MM])
    glycerol_spr_dip_first_bounce = vcsel_pos_x[turn_on_row] + 2*glass_thickness*np.tan(glycerol_theta_spr_rad)
    glycerol_spr_dip_first_bounce_x = np.array([glycerol_spr_dip_first_bounce, glycerol_spr_dip_first_bounce])
    glycerol_spr_dip_first_bounce_y = np.array([vcsel_glass_interface_y, vcsel_glass_interface_y - 0.1*MM])
    
    ## Plot
    scale = MM
    # plt.style.use('seaborn-v0_8-dark')
    plt.figure(1, figsize=(figure_width, figure_height))
    
    ## Extent of sensor  (Set smaller then it really is)
    plt.plot(extent_sensor/scale, np.ones(len(extent_sensor))*vcsel_glass_interface_y/scale, 'blue', linewidth=0.3)
    plt.plot(extent_sensor/scale, -np.ones(len(extent_sensor))*glass_thickness/scale, 'blue', linewidth=0.3)
    
    ## Vcsel chip extent and vcsel positions
    plt.plot(chip_size/scale, np.ones(len(chip_size))*vcsel_glass_interface_y/scale, 'black')
    plt.scatter(vcsel_pos_x/scale, np.ones(len(vcsel_pos_x))*vcsel_glass_interface_y/scale, color='black')
    
    ## Position of gold SPR surface
    plt.plot(gold_sensor_x/scale, gold_sensor_y/scale, 'yellow')
    plt.plot(gold_lines_x/scale, gold_lines_y/scale, 'yellow')
    
    
    ## Rays from laser
    plt.plot(center_ray_x/scale, center_ray_y/scale, 'r', label=r'Center ray')
    plt.plot(upper_ray_x/scale, upper_ray_y/scale, '--', color='black')
    plt.plot(lower_ray_x/scale, lower_ray_y/scale, '--', color='black')
    
    ## Different spr dips
    plt.plot(water_spr_x/scale, water_spr_y/scale, 'aqua', label=f'SPR dip $n={n_low}$')
    plt.plot(water_spr_first_bounce_x/scale, water_spr_first_bounce_y/scale, 'aqua')
    plt.plot(glycerol_spr_x/scale, glycerol_spr_y/scale, 'green', label=f'SPR dip $n={n_high}$')
    plt.plot(glycerol_spr_dip_first_bounce_x/scale, glycerol_spr_dip_first_bounce_y/scale, 'green')
    
    
    plt.title(r'VCSEL chip Katarina', fontsize=fontsize_title)
    plt.xlabel(r'x [mm]', fontsize=fontsize_label)
    plt.ylabel(r'y [mm]', fontsize=fontsize_label)
    
    
    plt.xticks(fontsize=fontsize_ticks)
    plt.yticks(fontsize=fontsize_ticks)
    plt.grid(linewidth=1, alpha=0.3)
    plt.tight_layout()
    plt.legend(fontsize=fontsize_legend)