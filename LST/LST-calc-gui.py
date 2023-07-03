import datetime
import math
import tkinter as tk
from tkinter import ttk

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

# Function to handle dropdown selection change
def on_dropdown_change(event):
    selected_longitude = dropdown_var.get()
    longitude = longitude_options[selected_longitude]
    update_clock(longitude)

# Function to update the LST clock label
def update_clock(longitude):
    hours, minutes, seconds = calculate_lst(longitude, datetime.datetime.now())
    clock_label.config(text=f"Local Sidereal Time (LST): {hours:02d}:{minutes:02d}:{seconds:02d}")
    root.after(1000, update_clock, longitude)

# Create the main window
root = tk.Tk()
root.title("LST Calculator")

# Create the clock label
clock_label = tk.Label(root, font=("Helvetica", 24))
clock_label.pack(pady=20)

# Create the dropdown menu
longitude_options = {
    "I-LOFAR": -7.9219,  #
    "LOFAR-SE": 11.93029,  #
}
dropdown_var = tk.StringVar()
dropdown = ttk.Combobox(root, textvariable=dropdown_var, values=list(longitude_options.keys()))
dropdown.bind("<<ComboboxSelected>>", on_dropdown_change)
dropdown.pack()

# Set the default selection for the dropdown
dropdown_var.set(list(longitude_options.keys())[0])

# Start updating the clock with the default longitude
selected_longitude = dropdown_var.get()
longitude = longitude_options[selected_longitude]
update_clock(longitude)
# update_clock()


# Run the main event loop
root.mainloop()
