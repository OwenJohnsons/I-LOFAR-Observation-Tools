#%% 
import numpy as np
import matplotlib.pyplot as plt
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.time import Time
import datetime
import astropy.units as u
import scienceplots 
plt.style.use(['science', 'no-latex'])
from matplotlib.collections import LineCollection
import matplotlib.dates as mdates

# ------------------------------------
#          - Set up Observer -
# ------------------------------------

longitude = 7.9219 * u.deg
latitude = 53.0950 * u.deg
elevation = 72.0 * u.m
location = EarthLocation.from_geodetic(longitude, latitude, elevation)


current_time = Time(datetime.datetime.now())

# Generate a time range for the next 24 hours
hours = np.linspace(0, 24, 100)  
times = current_time + hours * u.hour
utc_times = times.datetime

# Galactic Center coordinates
galactic_center = SkyCoord(ra=266.4051, dec=-29.0078, unit="deg", frame="icrs")

altitudes = []
azimuths = []

for time in times:
    altaz_frame = AltAz(obstime=time, location=location)
    altaz = galactic_center.transform_to(altaz_frame)
    altitudes.append(altaz.alt.deg)
    azimuths.append(altaz.az.deg)

plt.figure(figsize=(10, 6), dpi=150)

points = np.array([mdates.date2num(utc_times), altitudes]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)
norm = plt.Normalize(min(azimuths), max(azimuths))
lc = LineCollection(segments, cmap='viridis', norm=norm, linewidths=3)
lc.set_array(np.array(azimuths))
line = plt.gca().add_collection(lc)

plt.colorbar(line, label="Azimuth (degrees)")
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=4))
plt.xlim(utc_times[0], utc_times[-1])
plt.ylim(min(altitudes) - 5, max(altitudes) + 5)
plt.xlabel("Time (UTC)")
plt.ylabel("Altitude (degrees)")
plt.title("Galactic Center for next day starting at %s" % current_time.datetime.strftime("%H:%M, %m-%d "))
plt.grid(True)
plt.tight_layout()
plt.show()



