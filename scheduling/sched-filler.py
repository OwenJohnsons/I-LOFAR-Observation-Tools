
'''
Code Purpose: 
Author: Owen A. Johnson 
Date: 31/12/2023
'''
#%% 

import matplotlib.pyplot as plt
import smplotlib
# import scienceplots; plt.style.use('science')
import astropy.units as u
import numpy as np
import pandas as pd

from astropy.coordinates import EarthLocation, SkyCoord, solar_system_ephemeris, get_body, AltAz
from pytz import timezone
from astropy.time import Time
from astroplan import Observer
from astroplan import FixedTarget
from astroplan.plots import plot_sky
from LSTfunctions import calculate_lst, read_src
import matplotlib.dates as mdates
from tqdm import tqdm 
from datetime import datetime

# ------------------------------------
#          - Set up Arguments -
# ------------------------------------
plot = False; verbose = True

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def find_changes(iterable):
    changes = []
    for i in range(1, len(iterable)):
        if iterable[i] != iterable[i - 1]:
            changes.append(i)
    return changes

def schedule_timefmt(input_string):
    input_format = "%Y-%m-%d %H:%M:%S.%f"

    dt_object = datetime.strptime(input_string, input_format)
    output_format = "%Y-%m-%dT%H:%M"
    output_string = dt_object.strftime(output_format)

    return output_string

# ------------------------------------
#          - Set up Observer -
# ------------------------------------

# Set up Observer, Target and observation time objects.
longitude = 7.9219 * u.deg
latitude = 53.0950 * u.deg
elevation = 72.0 * u.m
location = EarthLocation.from_geodetic(longitude, latitude, elevation)

observer = Observer(name='I-LOFAR',
               location=location,
               pressure=0.615 * u.bar,
               relative_humidity=0.11,
               temperature=0 * u.deg_C,
               description="LOFAR Station IE613")

obs_window = 31
observe_time = Time.now()
observe_times = observe_time + np.linspace(0, obs_window, 1000)*u.hour
increment = round((60/(obs_window**2/100)/2))

# ------------------------------------
#          - Benchmark Targets -
# ------------------------------------

# - Polaris -
coordinates = SkyCoord('02h31m49.09s', '+89d15m50.8s', frame='icrs')
polaris = FixedTarget(name='Polaris', coord=coordinates)
polaris_style = {'color': 'k', 'marker': '*'}

# - Crab Pulsar - 
coordinates = SkyCoord('05h34m31.93830s', '+22d00m52.1758s', frame='icrs')
crab = FixedTarget(name='Crab', coord=coordinates)
crab_style = {'color': 'r'}

# - Sun - 
with solar_system_ephemeris.set('builtin'):
    sun_coords = get_body('sun', observe_times, location) 
sun = FixedTarget(name='Sun', coord=sun_coords)
sun_style = {'color': 'y'}

#%%
# -----------------------------------------------------------
#          - Altitude and Azimuth Calculations -
# -----------------------------------------------------------
src_df = pd.read_csv('2obs.csv')
src_names = src_df['Name']
coords = SkyCoord(ra=src_df['RA'], dec=src_df['DEC'], unit=(u.rad, u.rad))
alt_az_coords = [] 

print('Number of sources in the database: ', len(src_names))

for i in tqdm(range(len(coords))):
    alt = coords[i].transform_to(AltAz(obstime=observe_times, location=location)).alt.degree
    az = coords[i].transform_to(AltAz(obstime=observe_times, location=location)).az.degree
    alt_az_coords.append([[alt, az], src_names[i], coords[i]])
#%%
#  - Finding Highest Alt at each Observation time -
highest_alt = []

for i in range(0, len(observe_times)): # loop through each obs time. 
    max_alt = 0
    for j in range(0, len(alt_az_coords)):
        alt_data = alt_az_coords[j][0][0]
        if max_alt < alt_data[i]:
            max_alt = alt_data[i]
            src_name = alt_az_coords[j][1]
            src_coord = alt_az_coords[j][2]
    highest_alt.append([src_name, src_coord, max_alt, observe_times[i]])


change_idxs = [0] 
for i in range(1, len(highest_alt)):
    if highest_alt[i][1] != highest_alt[i - 1][1]:   
        change_idxs.append(i)
change_idxs.append(999)
len(change_idxs)

# ------------------------------------
#    - Printing Results in Format -
# ------------------------------------

for i in range(0, len(change_idxs) - 1):
    # Find matching id in the dataframe
    name_id = src_df.loc[src_df['Name'] == highest_alt[change_idxs[i]][0]].index[0]
    print(schedule_timefmt(str(highest_alt[change_idxs[i]][3])), '-', schedule_timefmt(str(highest_alt[change_idxs[i + 1]][3])), ': %s' % src_df['Name'][name_id], "[%s, %s, 'J2000']" % (src_df['RA'][name_id], src_df['DEC'][name_id]))
    
#%%
# ------------------------------------
#        - Plotting Results -
# ------------------------------------
plot_sky(polaris, observer, observe_time, style_kwargs=polaris_style)
plot_sky(crab, observer, observe_times, style_kwargs=crab_style)
plot_sky(sun, observer, observe_times, style_kwargs=sun_style)

# for i in range(0, len(highest_alt)):
#     trgt = FixedTarget(name=str(highest_alt[i][0]), coord=highest_alt[i][1])
#     start_time = int(highest_alt[i][3] - increment); end_time = int(highest_alt[i][3] + increment)
#     if start_time < 0: start_time = len(observe_time) - abs(start_time)
#     plot_sky(trgt, observer, observe_times[start_time:end_time], style_kwargs={'s': 10})

ax = plt.gca()
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 2, box.height * 2])

plt.legend(loc='center left', bbox_to_anchor=(1.25, 0.5))
plt.tight_layout()
plt.show()