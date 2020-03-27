#!/usr/bin/python3.5
import sys,math
import numpy as np
from metpy.calc import potential_temperature
from metpy.units import units

class potential_vorticity:


    def latlon(self,ni,nj,lat1,lat2,lon1,lon2):
        lon = np.empty(ni)
        lat = np.empty(nj)
        lon[0] = lon1
        lon[-1] = lon2
        if (lon1 < 0.0):
            lon[1] = lon[1]  + 360.0
        if (lon2 <= 0.0):
            lon[-1] = lon[-1]+360.0
        for i in range(0, ni):
            lon[i] = lon[0] + float(i)*(lon[-1] - lon[0])/float(ni-1)
            if (lon[i] > 180.0):
                lon[i] = lon[i] - 360.

        lon = lon[::-1]
        lat[0] = lat1
        lat[-1] = lat2

        if (lat2 > 90.0):
            lat[-1] = 180. - lat[-1]
        if (lat2 < -90.0):
            lat[-1] = -180.0 - lat[-1]
        if (lat1 > 90.0):
            lat[0] = 180. - lat[0]
        if (lat1 < -90.0):
            lat[0] = -180.0 - lat[0]

        for j in range(1,nj):
            lat[j] = lat[0] + float(j)* (lat[-1] - lat[0])/float(nj-1)
            if (lat[j] > 90.0):
                lat[j] = 180.0  - lat[j]
            if (lat[j] < -90.0):
                lat[j] = -180.0 - lat[j]
        if (lat[1] - lat[0] < 0):
            lat = lat[::-1]
        return (lat,lon)

    def ddx(self,s,lat,lon,missingData):
        lonLen = len(lon)
        latLen = len(lat)
        dsdx = np.empty((latLen,lonLen))
        rearth = 6371221.3

        di = abs(rearth*(np.radians(lon[1]-lon[0])))
        # GRIB order - S-N(OUTER)
        #              W-E(INNER)
        for j in range(0,latLen):                
            for i in range(1, lonLen-1):
                if (abs(lat[j]) >= 90.0):
                    dsdx[j,0] = 0.0
                elif (s[j, i+1] > -999.99 and s[j,i-1] > -999.99):
                    dsdx[j, i] = (s[j,i+1] - s[j,i-1])/(2.*di)
                elif (s[i+1,j] < -999.99 and s[j,i-1] > -999.99 and s[j,i] > -999.99):
                    dsdx[j,i] = (s[j,i] - s[j,i-1])/di
                elif (s[j,i+1] > -999.99 and s[j,i-1] < -999.99 and s[j,i] > -999.99):
                    dsdx[j,i]  = (s[j,i+1] - s[j,i])/di
                else:
                    dsdx[j,i] = -999.99

        for j in range(0,latLen):
            if (abs(lat[j]) >= 90.0):
                dsdx[j,0] = 0.0
                dsdx[j,-1] =0.0
            elif (np.allclose(2*lon[0]-lon[-1],lon[1],1e-3) or np.allclose(2*lon[0]-lon[-1],lon[1] + 360.0,1e-3)):
                if (s[j, 1] > -999.99 and s[j, -1] > -999.99):
                    dsdx[j, 0] = (s[j, -1] - s[j,1]) / (2.*di)
                elif (s[j,1] < -999.99 and s[j,-1] > -999.99 and s[j,0] > -999.99) :
                    dsdx[j,0] = (s[j,-1] - s[j,1]) / di
                elif (s[j, 1] > -999.99 and s[j,-1] > -999.99 and s[j,0] > -999.99):
                    dsdx[j,0] = (s [j,0] - s[j,1]) /di
                else:
                    dsdx[j, 0] = -999.99
                if (s[j,0] > -999.99 and s[j,-2] > -999.99):
                    dsdx[j,-1] = (s[j, -2] - s[j,0]) / (2. * di)
                elif (s[j,0] < -999.99 and s[j,-2] > -999.99 and s[j,-1] > -999.99):
                    dsdx[j,-1] = (s[j,-2] - s[j,-1]) / di
                elif (s[j,0] > -999.99 and s[j,-2] < -999.99 and s[j,-1] > -999.99) :
                    dsdx[j,-1] = (s[j,-1] - s[j,1]) / di
                else:
                    dsdx[j, -1] = -999.99
            elif (np.allclose(lon[0],lon[-1],1e-3)):
                if (s[j, 1] > -999.99 and s[j,-2] > -999.99) :
                    dsdx[j,0] = (s[j,-2] - s[j,1]) / (2. * di)
                elif (s[j,1] < -999.99 and s[j,-2] > -999.99 and s[j,0] > -999.99) :
                    dsdx[j,0] = (s[j,-2] - s[j,0]) / di
                elif (s[j, 1] > -999.99 and s[j, -2] < -999.99 and s[j, 0] > -999.99):
                    dsdx[j,0] = (s[j,1] - s[j,0]) / di
                else:
                    dsdx[j,0] = -999.99
                dsdx[j,-1] = dsdx[j,0]
            else:
                if (s[j, 1] > -999.99 and s[j,0] > -999.99) :
                    dsdx[j,0] = (s[j,0] - s[j,1]) /di
                else:
                    dsdx[j,0] = -999.99
                
                if (s[j,-1] > -999.99 and s[j,-2] > -999.99):
                    dsdx[j,-1] = (s[j,-2] -s[j,-1]) /di
                else:
                    dsdx[j,-1] = -999.99
        return dsdx

    def ddy(self,s,lat,lon,missingData):
        lonLen = len(lon)
        latLen = len(lat)
        dsdy = np.empty((latLen,lonLen))
        rearth = 6371221.3
        dj = abs(np.radians((lat[0]-lat[1])) * rearth)

        # North Pole 
        for i in range(0,lonLen):
            if (s[0,i] > -999.99 and s[1,i] > -999.99):
                # Make sure derivative is  dq/dy = [q(north) - q(south)]/dlat
                dsdy[0,i] = (s[1,i] - s[0,i])/dj
            else:
                dsdy[0,i] = -999.99
        # South Pole
        for i in range(0,lonLen):
            if (s[-1,i] > -999.99 and s[-2,i] > -999.99):
                # Make sure derivative is  dq/dy = [q(north) - q(south)]/dlat
                dsdy[-1,i] = (s[-1,i] - s[-2,i])/dj
            else:
                dsdy[-1,i] = -999.99
                        
        #Interior grid point
        for j in range(1,latLen-1):
            for i in range(0,lonLen):
                if (s[j-1,i] > -999.99 and s[j+1,i] > -999.99):
                    # Make sure derivative is  dq/dy = [q(north) - q(south)]/dlat
                    dsdy[j,i] = (s[j+1,i] - s[j-1,i])/(2.0*dj)
                elif (s[j-1,i] < -999.99 and s[j+1,i] > -999.99 and s[j,i] > -999.99):
                    dsdy[j,i] = (s[j+1,i] - s[j,i])/dj
                elif (s[j-1,i] > -999.99 and s[j+1,i] < -999.99 and s[j,i] > -999.99):
                    dsdy[j,i] = (s[j,i] - s[j-1,i])/dj
                else:
                    dsdy[j,i] = -999.99

        return dsdy

    def relvor(self,ni,nj,lat,lon,u,v,dvdx,dudy):

        lonLen = len(lon)
        latLen = len(lat)
        rearth = 6371221.3
        relv = np.empty((nj,ni))

        missing = 0
        # Begin North Pole
        for i in range(0,lonLen):
            if (u[1,i] > -999.99):
                relv[0,0] = u[1,i]
                break
            else:
                missing = i
        for i in range(missing+2,lonLen):
            if (u[1,i] > -999.99):
                relv[0,0] = relv[0,0]+u[1,i]
            else:
                missing = missing +1
        if (abs(lon[0] - lon[-1]) > .0001) :
            if (u[-1,1] > -999.99):
                relv[0,0]= relv[0,0]+u[-1,1]
            else:
                missing = missing +1
            relv[0,0] = relv[0,0]* math.cos(math.radians(lat[1]))/(1.-math.sin (math.radians(lat[1])))/rearth /float(lonLen - missing)
        else:
            relv[0,0] = relv[0,0]* math.cos(math.radians(lat[1]))/(1.-math.sin (math.radians(lat[1])))/rearth /float(lonLen -1- missing)
        for i in range(1,lonLen):
            relv[0,i] = relv[0,0]
        #Begin  South Pole
        missing = 0
        for i in range(0,lonLen):
            if (u[-2,i] > -999.99):
                relv[-1,-1] = u[-2,i]
                break
            else:
                missing = i
        for i in range(missing+2,lonLen):
            if (u[-2,i] > -999.99) :
                relv[-1,-1] = relv[-1,-1]+u[-2,i]
            else:
                missing = missing +1
        if (abs(lon[0] - lon[-1] > .001)):
            if(u[-2,i] > -999.99):
                relv[-1,-1]=relv[-1,-1]+u[-2,-1]
            else:
                missing = missing + 1
            relv[-1,-1]=relv[-1,-1]* np.cos(np.radians(lat[-2]))/(1.-np.sin(np.radians(lat[-2])))/rearth /float(lonLen -1- missing)
        else:
            relv[-1,-1]=relv[-1,-1]* np.cos(math.radians(lat[-2]))/(1.-np.sin (np.radians(lat[-2])))/rearth /float(lonLen - 2-missing)        
        for i in range(0,lonLen-1):
            relv[-1,i] = relv[-1,-1]


        # Global
        for j in range(1,latLen-1):
            for i in range(0,lonLen):
                if (u[j,i] < -999.99 or dvdx[j,i] < -999.99 or dudy[j,i] < -999.99 ):
                    relv[j,i] = -999.99
                else:
                    relv[j,i] = dvdx[j,i]-dudy[j,i]+(u[j,i]*np.tan(np.radians(lat[j])))/rearth
        return relv

    
    def absvor(self,lat,lon,relv):

        
        lonLen = len(lon)
        latLen = len(lat)
        absv = np.empty((latLen,lonLen))
        omega = 7.29212e-5
        for j in range(0,latLen):
            for i in range(0,lonLen):
                if (relv[j,i] > -999.99):
                    corl = 2.0 * omega *math.sin(math.radians(lat[j]))
                    absv[j,i] = relv[j,i]+corl
                else:
                    absv[j,i] = -999.99
        return absv

    def pot(self,tmp,pres):
        cp = 1004.0
        md = 28.9644
        R = 8314.41
        Rd = R/md

        pot = tmp * (100000./pres) ** (Rd/cp)

        return pot
    
    def pvonp(self,ni,nj,lat,lon,pres,pres1,pres2,tmp,tmp1,tmp2,u,u1,u2,v,v1,v2,missingData):

        cp = 1004.
        gravity = 9.80665
        md = 28.9644
        R = 8314.41
        Rd = R/md
        kappa = Rd/cp

        #print(v)
        dvdx = self.ddx(v,lat,lon,missingData)
        dudy = self.ddy(u,lat,lon,missingData)
        #print(dudy)
        relv = self.relvor(ni,nj,lat,lon,u,v,dvdx,dudy)

        absv = self.absvor(lat,lon,relv)

        theta = np.empty_like(tmp,dtype=object)

        theta1 = np.empty_like(tmp1,dtype=object)
        theta2 = np.empty_like(tmp2,dtype=object)
        pres = float(pres)
        pres1 = float(pres1)
        pres2 = float(pres2)
        theta[:,:] = self.pot(tmp[:,:],pres1)
        theta1[:,:] = self.pot(tmp1[:,:],pres1)
        theta2[:,:] = self.pot(tmp2[:,:],pres2)

        dpotdx = self.ddx(theta,lat,lon,missingData)

        dpotdy = self.ddy(theta,lat,lon,missingData)

        lnp1p2 = np.log(pres1/pres2)
        dpi = -1. /(pres1 - pres2)
        pv = np.empty((nj,ni))
        for j in range(0,nj):
            for i in range(0,ni):
                stabl = (theta[j,i]/pres) *(np.log(tmp1[j,i]/tmp2[j,i])/lnp1p2 - kappa)

                du = u1[j,i] - u2[j,i]
                dv = v1[j,i] - v2[j,i]
                dth = theta1[j,i] - theta2[j,i]
                vorcor = (du * dpotdy[j,i] - dv * dpotdx[j,i])/dth
                pv[j,i] = gravity * (absv[j,i] +vorcor) * dth *dpi  *1e6

        for j in range(0,nj):
            if (abs(lat[j] - 90.) < 0.001):
                for i in range(1,ni-1):
                    pv[j,0] = pv[j,0]+pv[j,i]
            if (abs(lon[1] - lon[ni-1]) < 0.001):
                pv[j,0] = pv[j,0]/float(ni-1)
            else:
                pv[j,0] = pv[j,0]+pv[j,-1]
                pv[j,0] = pv[j,0]/float(ni-1)
        k = 0
        m = 0
        for j in range(0,nj):
            for i in range(0,ni):
                #print(lon[i],lat[j],pv[j,i])
                if (lat[j] > 0.0  and pv[j,i] <= 0.):
                    print(lon[i],lat[j],pv[j,i])
                    k += 1
                elif (lat[j] < 0.0  and pv[j,i] >= 0.):
                    print(lon[i],lat[j],pv[j,i])
                    m += 1
        print(k,m)

        return pv

    def pvlayr(self,ni,nj,lat,lon,pres,pres1,pres2,tmp1,tmp2,u1,u2,v1,v2):
        
        cp = 1004.
        gravity = 9.80665
        md = 28.9644
        R = 8314.41
        Rd = R/md
        kappa = Rd/cp

        pres1 = float(pres1)
        pres2 = float(pres2)
        lnp1 = np.log(pres1)
        lnp2 = np.log(pres2)
        pav = (pres1*lnp1+pres2*lnp2)/(lnp1+lnp2)

        uav = np.empty((nj,ni))
        vav = np.empty((nj,ni))
        potav = np.empty((nj,ni))
        for j in range(0,nj):
            for i in range(0,ni):
                uav[j,i] = (lnp2*u2[j,i] + lnp1*u1[j,i])/(lnp1+lnp2)
                vav[j,i] = (lnp2*v2[j,i] + lnp1*v1[j,i])/(lnp1+lnp2)
                tav = np.exp((lnp2*np.log(tmp2[j,i]) + lnp1*np.log(tmp1[j,i]))/(lnp1+lnp2))
                potav[j,i] = self.pot(tav,pav)
        missingData = float(-999.99)
        dvdx = self.ddx(vav,lat,lon,missingData)
        dudy = self.ddy(uav,lat,lon,missingData)
        relv = self.relvor(ni,nj,lat,lon,uav,vav,dvdx,dudy)
        absv = self.absvor(lat,lon,relv)
        dpotdx = self.ddx(potav,lat,lon,missingData)
        dpotdy = self.ddy(potav,lat,lon,missingData)
        pv = np.empty((nj,ni))
        for j in range(0,nj):
            for i in range(0,ni):
                stabl = potav[j,i]/pav * (np.log(tmp1[j,i]/tmp2[j,i])/(lnp1-lnp2)-kappa)
                vorcor = ((v1[j,i] - v2[j,i])*dpotdx[j,i]-(u1[j,i] - u2[j,i])*dpotdy[j,i])/(self.pot(tmp1[j,i],pres1)-self.pot(tmp2[j,i],pres2))
                pv[j,i] = -gravity * (absv[j,i]+vorcor) * stabl * 1e6
        k = 0
        m = 0
        for j in range(0,nj):
            for i in range(0,ni):
                if (lat[j] > 0.0 and pv[j,i] <= 0.):
                    print(lat[j],pv[j,i])
                    k += 1
                elif (lat[j] < 0.0 and pv[j,i] >= 0.):
                    print(lat[j],pv[j,i])
                    m += 1
        print(k,m)
        sys.exit()
                
        for i in range(0,ni):
            pv[0,0]=pv[0,0]+pv[i,0]
            pv[0,-1] =pv[0,-1]+pv[i,-1]
        if (abs(lon[0] - lon[-1]) < 0.001):
            pv[0,0] = pv[0,0]/float(ni-2)
            pv[0,-1] = pv[0,-1]/float(ni-2)
        else:
            pv[0,0] = pv[0,0]+pv[-1,0]
            pv[0,0] = pv[0,0]/float(ni-1)
            pv[0,-1] = pv[0,-1]+pv[-1,-1]
            pv[0,-1] = pv[0,-1]/float(ni-1)

        for i in range(1,ni):
            pv[i,0] = pv[0,0]
            pv[i,-1] = pv[0,-1]

        return pv

    def ipv(ni,nj,lat,lon,kthta,thta,pthta,uthta,vthta):

        cp = 1004.
        gravity = 9.80665
        md = 28.9644
        R = 8314.41
        Rd = R/md
        kappa = Rd/cp

        for k in range(0,kthta):

            dvdx = self.ddx(vthta,ni,nj,lat,lon)
            dudy = self.ddy(uthta,ni,nj,lat)
            relv = self.relvor(ni,nj,lat,lon,uthta,dvdx,dudy)
            absv = self.absvor(ni,nj,lat,relv)
            for j in range(0,nj):
                for i in range(0,ni):
                    if (k ==1):
                        if (pthta[i,j,k] <= 0.0 or pthta[i,j,k+1] <= 0.0 or absvor[i,j] < -9998.0):
                            ipv[i,j,k] = -999.99
                        else:
                            tdwn = thta[k] * (pthta[i,j,k]/10000.0)**kappa
                            tup = thta[k+1]*(pthta[i,j,k+1]/10000.0)**kappa
                            expr1 = np.log(float(tup/tdwn))
                            expr2 = np.log(pthta[i,j,k+1]/pthta[i,j,k])
                            expr = (expr1 /expr2) - kappa
                            stabl = thta[k]/pthta[i,j,k] *expr
                            ipv[i,j,k] = -gravity * absvor[i,j] * stabl
                    elif (k == kthta):
                        if (pthta[i,j,k] <= 0.0 or pthta[i,j,k-1] <= 0.0 or absvor[i,j] < -999.99):
                            ipv[i,j,k] = -999.99
                        else:
                            tdwn = thta[k-1] * (pthta[i,j,k-1]/10000.0)**kappa
                            tup = thta[k]*(pthta[i,j,k]/10000.0)**kappa
                            expr1 = np.log(float(tup/tdwn))
                            expr2 = np.log(pthta[i,j,k]/pthta[i,j,k-1])
                            expr = (expr1 /expr2) - kappa
                            stabl = thta[k]/pthta[i,j,k] *expr
                            ipv[i,j,k] = -gravity * absvor[i,j] * stabl
                    else:
                        if (pthta[i,j,k+1] > 0.0 or pthta[i,j,k-1] > 0.0 or absvor[i,j] > -9998.0):
                            tdwn = thta[k-1] * (pthta[i,j,k-1]/10000.0)**kappa
                            tup = thta[k+1]*(pthta[i,j,k+1]/10000.0)**kappa
                            expr1 = np.log(float(tup/tdwn))
                            expr2 = np.log(pthta[i,j,k+1]/pthta[i,j,k-1])
                            expr = (expr1 /expr2) - kappa
                            stabl = thta[k]/pthta[i,j,k] *expr
                            ipv[i,j,k] = -gravity * absvor[i,j] * stabl
                        elif (pthta[i,j,k+1] <= 0.0 or pthta[i,j,k-1] > 0.0 or absvor[i,j] > -9998.0):
                            tdwn = thta[k-1] * (pthta[i,j,k-1]/10000.0)**kappa
                            tup = thta[k]*(pthta[i,j,k]/10000.0)**kappa
                            expr1 = np.log(float(tup/tdwn))
                            expr2 = np.log(pthta[i,j,k]/pthta[i,j,k-1])
                            expr = (expr1 /expr2) - kappa
                            stabl = thta[k]/pthta[i,j,k] *expr
                            ipv[i,j,k] = -gravity * absvor[i,j] * stabl
                            
                        elif (pthta[i,j,k+1] > 0.0 or pthta[i,j,k-1] <= 0.0 or absvor[i,j] > -9998.0):
                            tdwn = thta[k] * (pthta[i,j,k]/10000.0)**kappa
                            tup = thta[k+1]*(pthta[i,j,k+1]/10000.0)**kappa
                            expr1 = np.log(float(tup/tdwn))
                            expr2 = np.log(pthta[i,j,k]/pthta[i,j,k-1])
                            expr = (expr1 /expr2) - kappa
                            stabl = thta[k+1]/pthta[i,j,k] *expr
                            ipv[i,j,k] = -gravity * absvor[i,j] * stabl

                        else:
                            ipv[i,j,k] = -999.99    
        return ipv
