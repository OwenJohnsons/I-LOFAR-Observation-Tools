#%%
import datetime
import math
import numpy as np 
import argparse 
import astropy.units as u
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, get_sun
from astropy.time import Time

parser = argparse.ArgumentParser(description='Calculate LST for a given date and time')
parser.add_argument('--date', '-d', nargs='?', type=str, help='Date in the format YYYY-MM-DD:HH:MM', default=datetime.datetime.utcnow().strftime('%Y-%m-%d:%H:%M'))
parser.add_argument('--longitude', '-l', nargs='?', type=float, help='Longitude in degrees. Default I-LOFAR.', default=-7.9219)
parser.add_argument('--obs_window', '-obs_w', nargs='?', type=int, help='Observation window in hours.', default=28)
args = parser.parse_args()
obs_window = args.obs_window
date = args.date; longitude = args.longitude; obs_window = args.obs_window

# strip the date and time
date_time = datetime.datetime.strptime(date, '%Y-%m-%d:%H:%M')

# Constants
SOLAR_SIDEREAL_RATIO = 1.00273790935  # Ratio of solar day to sidereal day (approximately)

# --- Solar Ephemeris --

# Function to calculate Local Sidereal Time (LST)
def calculate_lst(longitude, date_time):
    # Convert the longitude to radians
    longitude_rad = math.radians(longitude)
    
    # Calculate the number of days since J2000.0 epoch
    j2000 = datetime.datetime(2000, 1, 1, 12, 0, 0)
    days_since_j2000 = (date_time - j2000).total_seconds() / (24 * 60 * 60)
    
    # Calculate the Greenwich Mean Sidereal Time (GMST) in hours
    gmst_hours = 18.697374558 + 24.06570982441908 * days_since_j2000
    
    # Calculate the Local Mean Sidereal Time (LMST) in hours
    lmst_hours = gmst_hours + (longitude_rad * 12 / math.pi)
    
    # Normalize the LMST to be between 0 and 24 hours
    lst_hours = lmst_hours % 32
    
    # Convert LST to hours, minutes, and seconds
    hours = int(lst_hours)
    minutes = int((lst_hours * 60) % 60)
    seconds = int((lst_hours * 3600) % 60)
    
    return hours, minutes, seconds

def read_src(path):
    src_names = []; ras = []; decs = []; total_lines = []
    for line in open(path, 'r'):
        splt = line.split(' ')
        total_lines.append(line)
        src_names.append(splt[0][1:])
        ras.append(splt[1][1:-1])
        decs.append(splt[2][1:-1])
    
    print(f"Total number of sources in reference list: {len(src_names)}")

    mask = np.unique(src_names, return_index=True)[1]
    src_names = np.array(src_names)[mask]
    ras = np.array(ras)[mask]
    decs = np.array(decs)[mask]
    print(f"Total number of unique sources in reference list: {len(src_names)}")


    return src_names, ras, decs, total_lines

def find_nearest(value, array):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

names, ra_list, dec_list, src_lines = read_src('SRC_refs.txt')

# - Convert Coordinates to SkyCoord
coords = SkyCoord(ra=ra_list, dec=dec_list, unit=(u.rad, u.rad))
ra_hours = coords.ra.hour
birr_location = EarthLocation(lat=53.41291*u.deg, lon=longitude*u.deg, height=12*u.m)
observing_time = date_time

time_now = datetime.datetime.utcnow() 
hours, minutes, seconds = calculate_lst(longitude, time_now)
print(f"Current Local Sidereal Time at I-LOFAR (LST): {hours:02d}:{minutes:02d}:{seconds:02d}")
print('-------------------')
print('BEST MATCH FOR EACH TIME')
print('-------------------\n')
for i in range(2*obs_window):
    hours, minutes, seconds = calculate_lst(longitude, date_time + datetime.timedelta(minutes=i*30))
    # --- Find Closest Matching Zen Sep --- 
    iteration_time = date_time + datetime.timedelta(minutes=i*30)
    zenith_seperation = 90 - coords.transform_to(AltAz(obstime=iteration_time, location=birr_location)).alt.degree
    min_idx = zenith_seperation.argmin()

    print(f"{date_time + datetime.timedelta(minutes=i*30)} | (LST): {hours:02d}:{minutes:02d}:{seconds:02d} | (Closest Trgt) {src_lines[min_idx][0:-1]} | (Zenith Seperation) {zenith_seperation[min_idx]:.2f} deg")
#%%
print('-------------------')
print('TOP 5 CLOSEST ZENITH SEPERATION MATCHES')
print('-------------------\n')
for i in range(2*obs_window):
    # --- Find top seperation matches of LST ---
    iteration_time = date_time + datetime.timedelta(minutes=i*30)
    zenith_seperation = 90 - coords.transform_to(AltAz(obstime=iteration_time, location=birr_location)).alt.degree
    # sort array by decreasing zenith seperation
    idx = np.argsort(zenith_seperation)[0:5]
    
    print(f"\n{iteration_time} ---")
    for j in idx:
        print(f"{src_lines[j][0:-1]} | (Zenith Seperation) {zenith_seperation[j]:.2f} deg")
 #%%
print('\n-------------------')
print('SUN POSITIONS')
print('-------------------\n')
for i in range(2*obs_window):
    iteration_time = date_time + datetime.timedelta(minutes=i*30)
    sun_coord = get_sun(Time(iteration_time.strftime('%Y-%m-%dT%H:%M:%S')))
    sun_altaz = sun_coord.transform_to(AltAz(obstime=iteration_time, location=birr_location))
    zenith_seperation = 90 - sun_altaz.alt.degree
    print(f"{iteration_time} | (Sun Altitude) {sun_altaz.alt.degree:.2f} deg | (Zenith Seperation) {zenith_seperation:.2f} deg")
