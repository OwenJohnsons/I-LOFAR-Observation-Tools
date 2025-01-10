'''

'''
#%% 
import numpy as np
import matplotlib.pyplot as plt
from astropy import units as u
from astropy.coordinates import SkyCoord
import subprocess
from tqdm import tqdm

#%%
def fitting(x, y): 
    z = np.polyfit(x, y, 5)
    smoothing_x = np.linspace(0, 75, 1000)
    smoothing_y = np.polyval(z, smoothing_x)
    return smoothing_x, smoothing_y

def sens_limit(snr, tsys, Aeff, bandwidth, tobs): 
    num = snr*tsys*1380*2
    print(num)
    dom = (Aeff*(np.sqrt(2*tobs*bandwidth)))  
    print(dom)
    return num/dom

def conv_generation(long): 
# Galactic center coordinates
    gal_lat = np.linspace(0, 75, 20) * u.deg; gal_long = np.linspace(0, long, 20) * u.deg
    gc = SkyCoord(l=gal_long, b=gal_lat, frame='galactic')
    # plot the galactic center

    gc_radec = gc.transform_to('icrs')      
    ra_rad = gc_radec.ra.radian; dec_rad = gc_radec.dec.radian
    conv_temps = [] # mean convolved temperature

    lofar_bandwidth = 3.66e6 # Hz
    

    for i in tqdm(range(0, len(ra_rad))):

        command = 'python ./tsky_sefd_LOFAR_ilt.py --ra %s --dec %s' % (ra_rad[i], dec_rad[i])
        output = subprocess.check_output(command, shell=True).decode('utf-8')

        freq = []; conv_temp = []; raw_temp = []; diff_temp = []
        lines = output.strip().split('\n')

        for line in lines[4:]:
            # Split each line by tabs
            columns = line.split('\t')
            # print(columns)
            freq.append(float(columns[0].split(':')[0]))
            print(columns[0].split(':')[0]) 
            conv_temp.append(float(columns[2]))
            raw_temp.append(float(columns[4]))
            diff_temp.append(float(columns[6]))
        
        mean_conv_temp = np.mean(conv_temp)
        conv_temps = np.append(conv_temps, mean_conv_temp)

    Aeff = 2048
    pulse_width = 1# seconds
    period = 1 # seconds
    tobs_v = 60*80 
    return sens_limit(10, conv_temps, Aeff, lofar_bandwidth, tobs_v)
#%%
    

convK_0 = conv_generation(0)
convK_60 = conv_generation(60)
convK_120 = conv_generation(120)
convK_180 = conv_generation(180)
convK_240 = conv_generation(240)
convK_300 = conv_generation(300)
convK_360 = conv_generation(360)

#%% 
import scienceplots; plt.style.use(['science', 'ieee'])


gal_lat = np.linspace(0, 75, 20) * u.deg; gal_long = np.linspace(0, 0, 20) * u.deg
smoothing_x, smoothing_y = fitting(gal_lat.value, convK_0*1000)

# -- plot aitoff projection --- 
plt.figure()
plt.subplot(111, projection='aitoff')
plt.grid(True)
plt.plot(gal_long, gal_lat, 'o', markersize=2)
plt.xlabel('Galactic Longitude (deg)')
plt.ylabel('Galactic Latitude (deg)')

# convert to ra and dec radians 
gc = SkyCoord(l=gal_long, b=gal_lat, frame='galactic')
gc_radec = gc.transform_to('icrs')
ra_rad = gc_radec.ra.radian; dec_rad = gc_radec.dec.radian
plt.figure()
plt.grid(True)
plt.plot(ra_rad, dec_rad, 'o', markersize=2)
plt.xlabel('RA (radians)')
plt.ylabel('Dec (radians)')



plt.figure(figsize=(5, 4))

plt.plot(smoothing_x, smoothing_y, 'r--', label='$l = 0 $')

smoothing_x, smoothing_y = fitting(gal_lat.value, convK_60*1000)
plt.plot(smoothing_x, smoothing_y, 'b--', label='$l = 60 $')

smoothing_x, smoothing_y = fitting(gal_lat.value, convK_120*1000)
plt.plot(smoothing_x, smoothing_y, 'g--', label='$l = 120 $')

smoothing_x, smoothing_y = fitting(gal_lat.value, convK_180*1000)
plt.plot(smoothing_x, smoothing_y, 'y--', label='$l = 180 $')

smoothing_x, smoothing_y = fitting(gal_lat.value, convK_240*1000)
plt.plot(smoothing_x, smoothing_y, 'm--', label='$l = 240 $')

smoothing_x, smoothing_y = fitting(gal_lat.value, convK_300*1000)
plt.plot(smoothing_x, smoothing_y, 'c--', label='$l = 300 $')

# smoothing_x, smoothing_y = fitting(gal_lat.value, convK_360*1000)
# plt.plot(smoothing_x, smoothing_y, 'k--', label='$l = 360 $')


plt.xlabel('Galactic Latitude (deg)')
plt.ylabel('Sensitivity Limit (mJy)')
plt.legend(frameon=True)
plt.show()
# %%
