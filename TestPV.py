#!/usr/bin/python3.5
import sys,os
import numpy as np
from netCDF4 import Dataset,num2date
from PV import potential_vorticity
from cdo import Cdo

import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from cartopy.util import add_cyclic_point
import matplotlib as mpl
mpl.rcParams['mathtext.default'] = 'regular'
import matplotlib.pyplot as plt


def main():
    pv = potential_vorticity()
    #(lat,lon)=pv.latlon(144,73,90,-90,0,-2.5)
    #print(lat)
    #ni=144
    #nj = 73
    
    pres = ["100000","92500","85000","70000","60000","50000","40000","30000","25000","20000","15000","10000","7000","5000","3000","2000","1000"]
    tmp_file_list = [ file for file in os.listdir('.') if file.startswith("air") ]
    uwnd_file_list = [ file for file in os.listdir('.') if file.startswith("uwnd") ]
    vwnd_file_list = [ file for file in os.listdir('.') if file.startswith("vwnd") ]

    #Start
    tmpFilePressureLevelDictionary={}
    for file in tmp_file_list:
        pressureLevel = int(file.split("_")[1])
        tmpFilePressureLevelDictionary[pressureLevel] = file
    args = []
    missing  = 0
    for key in  sorted(tmpFilePressureLevelDictionary,reverse=True):
        file = tmpFilePressureLevelDictionary[key]
        nc_tempFile = Dataset(file,'r')
        lats = nc_tempFile.variables['lat'][:]  # extract/copy the data
        lons = nc_tempFile.variables['lon'][:]
        lats = lats[:].squeeze()
        lons = lons[:].squeeze()
        nj = len(lats)
        ni = len(lons)
        for name,variable in nc_tempFile.variables.items():
            for attrname in variable.ncattrs():
                #print(attrname)
                try:
                    if attrname ==  "missing_value":
                        missingData = variable.getncattr(attrname)
                        break
                except:
                    print("Missing Data Not Found")
        temp = nc_tempFile.variables['air'][:]
        temp = np.reshape(temp,(nj,ni,1))
        temp = temp[::-1,:,:]
        args.append(temp)
    tmp = np.concatenate(args,axis=2)

    #Start Uwind
    uwndFilePressureLevelDictionary={}
    for file in uwnd_file_list:
        pressureLevel = int(file.split("_")[1])
        uwndFilePressureLevelDictionary[pressureLevel] = file
    args = []
    for key in  sorted(uwndFilePressureLevelDictionary,reverse=True):
        file = uwndFilePressureLevelDictionary[key]
        nc_uwndFile = Dataset(file,'r')
        uwnd = nc_uwndFile.variables['uwnd'][:]
        uwnd = np.reshape(uwnd,(nj,ni,1))
        uwnd = uwnd[::-1,:,:]
        args.append(uwnd)
    u = np.concatenate(args,axis=2)
    #Done

    #Start VWind
    vwndFilePressureLevelDictionary={}
    for file in vwnd_file_list:
#        print(file)
        pressureLevel = int(file.split("_")[1])
        vwndFilePressureLevelDictionary[pressureLevel] = file
    args = []
    for key in  sorted(vwndFilePressureLevelDictionary,reverse=True):
#        print(key)
        file = vwndFilePressureLevelDictionary[key]
        nc_vwndFile = Dataset(file,'r')
        vwnd = nc_vwndFile.variables['vwnd'][:]
        vwnd = np.reshape(vwnd,(nj,ni,1))
        vwnd = vwnd[::-1,:,:]
        #slicelist = [slice(0, None)] * vwnd.ndim
        #slicelist[1] = slice(None, None, -1)
        #vwnd = vwnd.copy()[slicelist]
        #vwnd = np.flip(vwnd,1)
        args.append(vwnd)
    v = np.concatenate(args,axis=2)
    #Done
    lats = lats[::-1]
    pvor = np.empty((ni,nj))
    for k in range(0,17):
        #if (k == 0):
#            pvor = pv.pvonp(ni,nj,lat,lon,pres[k],pres[k+1],pres[k],tmp[:,:,k],tmp[:,:,k+1],tmp[:,:,k],u[:,:,k],u[:,:,k+1],u[:,:,k],v[:,:,k],v[:,:,k+1],v[:,:,k])
        #   print("NO")
        #elif (k == 16):
#            pvor = pv.pvonp(ni,nj,lat,lon,pres[k],pres[k-1],pres[k],tmp[:,:,k],tmp[:,:,k-1],tmp[:,:,k],u[:,:,k],u[:,:,k-1],u[:,:,k],v[:,:,k],v[:,:,k-1],v[:,:,k])
         #   print("NO")
        #else:
        if (k ==9):
            #print(pres[k],pres[k+1],pres[k-1])
            #pvor = pv.pvonp(ni,nj,lats,lons,pres[k],pres[k+1],pres[k-1],tmp[:,:,k],tmp[:,:,k+1],tmp[:,:,k-1],u[:,:,k],u[:,:,k+1],u[:,:,k-1],v[:,:,k],v[:,:,k+1],v[:,:,k-1],missingData)
            pvor = pv.pvlayr(ni,nj,lats,lons,pres[k],pres[k+1],pres[k-1],tmp[:,:,k+1],tmp[:,:,k-1],u[:,:,k+1],u[:,:,k-1],v[:,:,k+1],v[:,:,k-1])
            sys.exit()
            ax1 = plt.axes(projection=ccrs.PlateCarree(central_longitude=180))
            clevs = [-20,15,-10,-5,5,10,15,20]
            shear_fill = ax1.contourf(lon,lat,pvor,clevs,
                                      transform=ccrs.PlateCarree(), cmap=plt.cm.RdBu_r,
                                      extend='both')
            ax1.coastlines()
            ax1.gridlines()
            ax1.set_xticks([0, 60, 120, 180, 240, 300, 359.99], crs=ccrs.PlateCarree())
            ax1.set_yticks([-90, -60, -30, 0, 30, 60, 90], crs=ccrs.PlateCarree())
            lon_formatter = LongitudeFormatter(zero_direction_label=True,
                                               number_format='.0f')
            lat_formatter = LatitudeFormatter()
            ax1.xaxis.set_major_formatter(lon_formatter)
            ax1.yaxis.set_major_formatter(lat_formatter)
            plt.colorbar(shear_fill, orientation='horizontal')
            
            plt.title('Isobaric Potential Vorticity On The 200 hPa surface', fontsize=16)
            plt.savefig('pv.png')
            plt.show()
                
            


main()
