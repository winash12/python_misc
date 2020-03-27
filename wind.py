#importing Magics module
from Magics.macro import *
import pygrib
import numpy as np
import sys


file = 'download.grib'
grbs = pygrib.open(file)
grb_uwind = grbs.select()[0] #U 10m wind component 
grb_vwind = grbs.select()[1] #V 10m wind component 
data_uwind = grb_uwind.values #U 10m wind values in m/s
data_vwind = grb_vwind.values #V 10m wind values in m/s

windspeed = np.sqrt(np.square(data_uwind) + np.square(data_vwind))
print(windspeed.shape)


#Example reference
ref = 'windflag'

#Setting of the output file name
output = output(output_formats= ['png'],
output_name_first_page_number= 'off',
output_name= ref)

#Setting the coordinates of the geographical area
world = mmap(subpage_upper_right_longitude= 180.,
subpage_upper_right_latitude= 90.,
subpage_lower_left_longitude= -180.,
subpage_map_projection= 'cylindrical',
subpage_lower_left_latitude= -90.,
subpage_clipping = True)

#Background Coastlines
background = mcoast( map_coastline_sea_shade_colour= 'white',
map_coastline_land_shade_colour= 'cream',
map_grid= 'off',
map_coastline_land_shade= 'on',
map_coastline_sea_shade= 'on',
map_label= 'off',
map_coastline_colour="tan")

#Define the shading for the wind speed

#Import the wind at 200hPa uv200
uv = mgrib( grib_input_file_name = './download.grib',
grib_wind_position_1=1,grib_wind_position_2=2)

print(type(uv))
sys.exit()

uv_flags = mwind(
wind_field_type = "flags",
wind_thinning_factor = 20,
wind_flag_colour = "evergreen",
wind_flag_length = 0.25,
wind_flag_min_speed = 2.0,
wind_flag_origin_marker = "dot",
wind_advanced_method    = "on",    
wind_advanced_colour_selection_type      = 'interval',
wind_advanced_colour_level_interval      = 0.5,
#wind_advanced_colour_reference_level     = 20.0,
#wind_advanced_colour_max_value           = 100.0,
#wind_advanced_colour_min_value           = 20.0,
wind_advanced_colour_table_colour_method = 'calculate',
wind_advanced_colour_direction           = 'clockwise',
wind_advanced_colour_min_level_colour    = 'turquoise',
wind_advanced_colour_max_level_colour    = 'purple_red'
)

title = mtext( text_lines = ["Wind flags"],
text_justification = 'left',
text_font_size = 0.5,
text_colour = 'charcoal')

legend = mlegend(legend= 'on',
           legend_text_colour= 'charcoal',
           legend_box_mode= 'positional',
           legend_box_x_position= 27.5,
           legend_box_y_position= 4.,
           legend_box_x_length= 2.,
           legend_box_y_length= 12.,
           legend_border= 'off',
           legend_border_colour= 'charcoal',
           legend_box_blanking= 'on',
           legend_display_type= 'continuous',
           legend_title = 'on',
	   legend_title_text= 'Wind speed at surface level',
	   legend_text_font_size = '0.5')

#To the plot
plot(output, world, background, uv, uv_flags, title,legend)
