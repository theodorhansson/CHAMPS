import matplotlib.pyplot as plt
import numpy as np
from spr_calculation import SPR_ang, ResonantN, ref_idx

# if smoothing:
def mov_avg(data, window_size):
    # window_size = 1
    window = np.ones(window_size) / window_size
    data = np.convolve(data, window, mode='same')
    return data

names=[
       '0929_170046_Water_200',
       '0929_170728_Water_3pc_200',
       '0929_172025_3pc_Water_200',
       '0929_173250_Water_Air_200'
       ]

fig = plt.figure(figsize=(8,5))
ax = fig.add_subplot(111)
end_time =0
for name in names:
    data = np.genfromtxt(f'data/{name}/{name}_data.txt', delimiter=',')
    for i, datapoint in enumerate(data):
        data[i,1] = data[i,1] if data[i,1]>350 else data[i,1]+150
    ax.scatter(data[:,0]+end_time, data[:,1], label=name, marker='o', s=3, alpha=0.3)
    ax.plot(data[:,0]+end_time, mov_avg(data[:,1], 5), label=name+'_avg', linewidth=1)
    end_time += data[-1,0]

ax.legend(loc='upper left', fontsize=5)
    
ax.set_xlabel('Time, s')
ax.set_ylabel('SPR Coordinate, um')
ax.set_ylim([350,550])
ax.set_xlim([0,2000])
ax.grid(linewidth=0.2)
ax.set_xticks(np.arange(0,2000,60))
ax.set_xticklabels(ax.get_xticks(), rotation=90)

ax2 = ax.twinx()
ax2.set_ylabel('Refractive Index')
ylims = [ax.get_yticks()[0], ax.get_yticks()[-1]]
ref_indices = [ResonantN(theta_spr=SPR_ang((lim+4635)/1000)) for lim in ylims]
ax2.set_ylim(ref_indices)
ax2.set_yticks(np.round(np.arange(ref_indices[0],ref_indices[-1]+0.001,0.001),3))
ax2.axhline(ref_idx(0.00),color='b',linewidth=0.5,label='Water',linestyle='--')
ax2.axhline(ref_idx(0.03),color='r',linewidth=0.5,label='3% Glycerol', linestyle='--')
ax2.legend(fontsize=5)
plt.show()


fig = plt.figure(figsize=(8,5))
ax = fig.add_subplot(111)
end_time =0
for name in names:
    data = np.genfromtxt(f'data/{name}/{name}_data.txt', delimiter=',')
    for i, datapoint in enumerate(data):
        data[i,1] = data[i,1] if data[i,1]>350 else data[i,1]+150
    ax.scatter(data[:,0]+end_time, data[:,1], label=name, marker='o', s=3, alpha=0.3)
    ax.plot(data[:,0]+end_time, mov_avg(data[:,1], 5), label=name+'_avg', linewidth=1)
    end_time += data[-1,0]
    # ax.legend()
    
ax.set_xlabel('Time, s')
ax.set_ylabel('SPR Coordinate, um')
ax.set_ylim([473,479])
ax.set_xlim([750,880])

ax.set_xticks(np.arange(ax.get_xticks()[0],ax.get_xticks()[-1],5))
ax.set_xticklabels(ax.get_xticks(), rotation=90)

ax2 = ax.twinx()
ax2.set_ylabel('Refractive Index')
ylims = [ax.get_yticks()[0], ax.get_yticks()[-1]]
ref_indices = [ResonantN(theta_spr=SPR_ang((lim+4650)/1000)) for lim in ylims]
ax2.set_ylim(ref_indices)
ax2.set_yticks(np.arange(ref_indices[0],ref_indices[1],0.00001))
ax2.axhline(ref_idx(0.00),color='b',linewidth=0.5,label='Water')
ax2.axhline(ref_idx(0.03),color='r',linewidth=0.5,label='3% Glycerol')
# ax2.legend(loc='upper left')
ax2.grid(linewidth=0.2)
plt.show()