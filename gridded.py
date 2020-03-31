
import tropycal.tracks as tracks

import datetime as dt
import sys

import matplotlib.pyplot as plt

hurdat_atl = tracks.TrackDataset(basin='north_indian',source='ibtracs',ibtracs_mode="jtwc")

# Let's retrieve an instance of Hurricane Kyarr from 2019:

storm = hurdat_atl.get_storm(('vardah',2016))

###########################################
# This instance of Storm contains several methods that return the storm data back in different data types. The following examples will show # how to retrieve 3 different data types.
# 

print(storm.to_dict())

print(storm.to_xarray())

print(storm.to_dataframe())

ax = storm.plot(return_ax=True)
hurdat_atl.ace_climo(plot_year=2019,compare_years=2018,save_path="ace_climo.png")

hurdat_atl.wind_pres_relationship(storm=('kyarr',2019),save_path="wind_pres.png")

hurdat_atl.ace_climo(rolling_sum=30,plot_year=2019,compare_years=2018,save_path="rolling_sum.png")
hurdat_atl.hurricane_days_climo(plot_year=2019,save_path="no_of_days.png")
ax=hurdat_atl.gridded_stats(cmd_request="minimum_pressure",year_range=((2019,2019)),return_ax=True)
plt.savefig('minimum_pressure.png')
