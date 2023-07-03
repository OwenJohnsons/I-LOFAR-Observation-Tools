#%%
import datetime
import math

# Constants
SOLAR_SIDEREAL_RATIO = 1.00273790935  # Ratio of solar day to sidereal day (approximately)

# Function to calculate Local Sidereal Time (LST)
def calculate_lst(longitude, date_time):
    # Convert the longitude to radians
    longitude_rad = math.radians(longitude)
    
    # Get the current date and time in UTC
    utc_time = date_time.utcnow()
    
    # Calculate the number of days since J2000.0 epoch
    j2000 = datetime.datetime(2000, 1, 1, 12, 0, 0)
    days_since_j2000 = (utc_time - j2000).total_seconds() / (24 * 60 * 60)
    
    # Calculate the Greenwich Mean Sidereal Time (GMST) in hours
    gmst_hours = 18.697374558 + 24.06570982441908 * days_since_j2000
    
    # Calculate the Local Mean Sidereal Time (LMST) in hours
    lmst_hours = gmst_hours + (longitude_rad * 12 / math.pi)
    
    # Normalize the LMST to be between 0 and 24 hours
    lst_hours = lmst_hours % 24
    
    # Convert LST to hours, minutes, and seconds
    hours = int(lst_hours)
    minutes = int((lst_hours * 60) % 60)
    seconds = int((lst_hours * 3600) % 60)
    
    return hours, minutes, seconds

longitude = -7.9219  # Replace with your longitude in degrees
date_time = datetime.datetime.now()  # Replace with the desired date and time

hours, minutes, seconds = calculate_lst(longitude, date_time)
print(f"Local Sidereal Time (LST): {hours:02d}:{minutes:02d}:{seconds:02d}")
