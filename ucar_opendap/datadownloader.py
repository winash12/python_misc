import sys

import re

import netrc

from datetime import date,datetime,timedelta



import requests

from xml.etree import ElementTree

from urllib.request import urlopen

import math,requests

class OPeNDAPVariableCoverage:

    def getVariableTimeMap(self):
        pass

    def getTimeCoordinateForOPeNDAPVariable(self,atmosVariable):
        pass
    

class AtmosphericVariableCoverage(OPeNDAPVariableCoverage):

    
    def __init__(self,openDAPRequestObject):
        self.openDAPRequestObject = openDAPRequestObject
        self.openDAPNameSpace = openDAPRequestObject.get_opendap_namespace()
        self.url = openDAPRequestObject.get_URL()
        self.url =self.url + ".ddx"

        self.atmosVariableList = []
        self.variableIsobaricMap = {}
        self.variableTimeMap  = {}
    
        self.set_atmos_variables()
#        print(self.variableTimeMap)
        
    def set_atmos_variables(self):
        response = requests.get(self.url)
        tree = ElementTree.fromstring(response.content)
        self.set_opendapxmltree(tree)
        grid = tree.findall(self.openDAPNameSpace+"Grid")
        for el in grid:
            attr = el.findall(self.openDAPNameSpace+"Attribute")
            for child in attr:
                if child.get("name") == "coordinates":
                    val = child.find(self.openDAPNameSpace+"value")
                    value = val.text
                    if "isobaric" in value:
                        try:
                            isobaric = re.search('isobaric[0-9]|isobaric', value).group(0)
                            time = re.search('time[0-9]|time', value).group(0)
                            self.atmosVariableList.append(el.get("name"))
                            self.variableIsobaricMap[el.get("name")] = isobaric
                            self.variableTimeMap[el.get("name")] =time
                        except AttributeError:
                            print("XML Parsing Error")
    def set_opendapxmltree(self,tree):
        self.tree = tree

    def get_opendapxmltree(self):
        return self.tree

        
    def getAtmosVariables(self):
        return self.atmosVariableList

                            
    def getAtmosVariableIsobaricMap(self):
        return self.variableIsobaricMap

    def getIsobaricVariableForAtmosVariable(self,atmosVariable):
        return self.variableIsobaricMap[atmosVariable]
    
    def getVariableTimeMap(self):
        return self.variableTimeMap

    def getTimeCoordinateForOPeNDAPVariable(self,atmosVariable):
        return self.variableTimeMap[atmosVariable]

class SurfaceVariableCoverage(OPeNDAPVariableCoverage):

    
    def __init__(self,openDAPRequestObject,atmosCoverage):
        self.openDAPRequestObject = openDAPRequestObject
        self.openDAPNameSpace = openDAPRequestObject.get_opendap_namespace()

        urlSurface = openDAPRequestObject.get_URLSurface()

        if urlSurface:
            self.urlSurface = urlSurface
        self.surfaceVariableList = []
        self.variableTimeMap  = {}
        self.set_surface_variables(atmosCoverage)
        
    def set_surface_variables(self,atmosCoverage):
        if self.urlSurface:
            self.urlSurface =self.urlSurface + ".ddx"
            response = requests.get(self.urlSurface)
            tree = ElementTree.fromstring(response.content)
        else:
            tree = atmosCoverage.get_opendapxmltree()
        grid = tree.findall(self.openDAPNameSpace+"Grid")
        for el in grid:
            variable = el.get("name")
            if "surface" in variable:
                attr = el.findall(self.openDAPNameSpace+"Attribute")
                for child in attr:
                    if child.get("name") == "coordinates":
                        val = child.find(self.openDAPNameSpace+"value")
                        value = val.text
                        if "time" in value:
                            try:
                                time = re.search('time[0-9]|time', value).group(0)
                                self.surfaceVariableList.append(el.get("name"))
                                self.variableTimeMap[el.get("name")] =time
                            except AttributeError:
                                print("Error")

    def get_surface_variables(self):
        return self.surfaceVariableList

                            
    def getVariableTimeMap(self):
        return self.variableTimeMap

    def getTimeCoordinateForOPeNDAPVariable(self,surfaceVariable):
        return self.variableTimeMap[surfaceVariable]

class SpatialCoverage(OPeNDAPVariableCoverage):


    def __init__(self,grid_spacing):
        self.latList = []
        self.lonList = []
        self.grid_spacing = float(grid_spacing)
        self.setMinMaxLatRange()
        self.setMinMaxLonRange()

    def getLatIndex(self,latitude):
        return self.latList.index(latitude)

    def getLonIndex(self,longitude):
        return self.lonList.index(longitude)

    def setMinMaxLatRange(self):
        c = 90
        maxLatitude = math.ceil(181/self.grid_spacing)
        for counter in range(0,maxLatitude):
            self.latList.append(float(c))
       #     print(self.latList[counter])
            c -= self.grid_spacing
        return
        
    def setMinMaxLonRange(self):
        z = 0
        maxLongitude = math.ceil((360/self.grid_spacing))
        for counter in range(0,maxLongitude):
            self.lonList.append(float(z))
#            print(self.lonList[counter])
            z += self.grid_spacing
        return 

    
class ERA1SpatialCoverage(SpatialCoverage):


    def __init__(self):
        self.latList = []
        self.lonList = []
        self.setMinMaxLatRange()
        self.setMinMaxLonRange()

    def getLatIndex(self,latitude):
        return self.latList.index(latitude)

    def getLonIndex(self,longitude):
        return self.lonList.index(longitude)

    def setMinMaxLatRange(self):
        self.latList = [89.46282, 88.76695, 88.06697, 87.366066, 86.6648, 85.96337, 85.26185, 84.560265, 83.858635, 83.15699, 82.45532, 81.75363, 81.05194, 80.350235, 79.64853, 78.94681, 78.245094, 77.543365, 76.84164, 76.13991, 75.43818, 74.73644, 74.034706, 73.33297, 72.63123, 71.92949, 71.22775, 70.52601, 69.824265, 69.12252, 68.42078, 67.71903, 67.01729, 66.315544, 65.61379, 64.91205, 64.210304, 63.508553, 62.806805, 62.105057, 61.40331, 60.70156, 59.999813, 59.29806, 58.596313, 57.89456, 57.192814, 56.491062, 55.789314, 55.087563, 54.385815, 53.684063, 52.98231, 52.28056, 51.57881, 50.87706, 50.17531, 49.473557, 48.771805, 48.070053, 47.3683, 46.66655, 45.964798, 45.263046, 44.561295, 43.859543, 43.15779, 42.45604, 41.754288, 41.052536, 40.350784, 39.649033, 38.94728, 38.24553, 37.543777, 36.842022, 36.14027, 35.43852, 34.736767, 34.035015, 33.333263, 32.631508, 31.929756, 31.228004, 30.52625, 29.8245, 29.122746, 28.420994, 27.71924, 27.017488, 26.315735, 25.613983, 24.91223, 24.210478, 23.508724, 22.806973, 22.105219, 21.403465, 20.701714, 19.99996, 19.298208, 18.596455, 17.894701, 17.19295, 16.491196, 15.789443, 15.08769, 14.385937, 13.684184, 12.982431, 12.280678, 11.578925, 10.877172, 10.175419, 9.473666, 8.771913, 8.07016, 7.368407, 6.666654, 5.964901, 5.263148, 4.5613947, 3.8596418, 3.1578887, 2.4561357, 1.7543826, 1.0526296, 0.35087654, -0.35087654, -1.0526296, -1.7543826, -2.4561357, -3.1578887, -3.8596418, -4.5613947, -5.263148, -5.964901, -6.666654, -7.368407, -8.07016, -8.771913, -9.473666, -10.175419, -10.877172, -11.578925, -12.280678, -12.982431, -13.684184, -14.385937, -15.08769, -15.789443, -16.491196, -17.19295, -17.894701, -18.596455, -19.298208, -19.99996, -20.701714, -21.403465, -22.105219, -22.806973, -23.508724, -24.210478, -24.91223, -25.613983, -26.315735, -27.017488, -27.71924, -28.420994, -29.122746, -29.8245, -30.52625, -31.228004, -31.929756, -32.631508, -33.333263, -34.035015, -34.736767, -35.43852, -36.14027, -36.842022, -37.543777, -38.24553, -38.94728, -39.649033, -40.350784, -41.052536, -41.754288, -42.45604, -43.15779, -43.859543, -44.561295, -45.263046, -45.964798, -46.66655, -47.3683, -48.070053, -48.771805, -49.473557, -50.17531, -50.87706, -51.57881, -52.28056, -52.98231, -53.684063, -54.385815, -55.087563, -55.789314, -56.491062, -57.192814, -57.89456, -58.596313, -59.29806, -59.999813, -60.70156, -61.40331, -62.105057, -62.806805, -63.508553, -64.210304, -64.91205, -65.61379, -66.315544, -67.01729, -67.71903, -68.42078, -69.12252, -69.824265, -70.52601, -71.22775, -71.92949, -72.63123, -73.33297, -74.034706, -74.73644, -75.43818, -76.13991, -76.84164, -77.543365, -78.245094, -78.94681, -79.64853, -80.350235, -81.05194, -81.75363, -82.45532, -83.15699, -83.858635, -84.560265, -85.26185, -85.96337, -86.6648, -87.366066, -88.06697, -88.76695, -89.46282
]

    def setMinMaxLonRange(self):
        self.lonList = [0.0, 0.7031253, 1.4062506, 2.109376, 2.8125012, 3.5156264, 4.218752, 4.921877, 5.6250024, 6.328128, 7.031253, 7.7343783, 8.437504, 9.140629, 9.843754, 10.54688, 11.250005, 11.95313, 12.656256, 13.359381, 14.062506, 14.765632, 15.468757, 16.171883, 16.875008, 17.578133, 18.281258, 18.984383, 19.687508, 20.390635, 21.09376, 21.796885, 22.50001, 23.203135, 23.90626, 24.609385, 25.312511, 26.015636, 26.718761, 27.421886, 28.125011, 28.828136, 29.531263, 30.234388, 30.937513, 31.640638, 32.343765, 33.04689, 33.750015, 34.45314, 35.156265, 35.85939, 36.562515, 37.26564, 37.968765, 38.67189, 39.375015, 40.07814, 40.78127, 41.484394, 42.18752, 42.890644, 43.59377, 44.296894, 45.00002, 45.703144, 46.40627, 47.109394, 47.81252, 48.515644, 49.21877, 49.921898, 50.625023, 51.328148, 52.031273, 52.734398, 53.437523, 54.140648, 54.843773, 55.546898, 56.250023, 56.953148, 57.656273, 58.359398, 59.062527, 59.76565, 60.468777, 61.1719, 61.875027, 62.57815, 63.281277, 63.9844, 64.68753, 65.390656, 66.09378, 66.796906, 67.50003, 68.203156, 68.90628, 69.609406, 70.31253, 71.015656, 71.71878, 72.421906, 73.12503, 73.828156, 74.53128, 75.234406, 75.93753, 76.640656, 77.34378, 78.046906, 78.75003, 79.453156, 80.15628, 80.859406, 81.56254, 82.26566, 82.96879, 83.67191, 84.37504, 85.07816, 85.78129, 86.48441, 87.18754, 87.89066, 88.59379, 89.29691, 90.00004, 90.70316, 91.40629, 92.10941, 92.81254, 93.51566, 94.21879, 94.92191, 95.62504, 96.32816, 97.03129, 97.73441, 98.43754, 99.14067, 99.843796, 100.54692, 101.250046, 101.95317, 102.656296, 103.35942, 104.062546, 104.76567, 105.468796, 106.17192, 106.875046, 107.57817, 108.281296, 108.98442, 109.687546, 110.39067, 111.093796, 111.79692, 112.500046, 113.20317, 113.906296, 114.60942, 115.312546, 116.01567, 116.718796, 117.42193, 118.12505, 118.82818, 119.5313, 120.23443, 120.93755, 121.64068, 122.3438, 123.04693, 123.75005, 124.45318, 125.1563, 125.85943, 126.56255, 127.26568, 127.9688, 128.67194, 129.37506, 130.07819, 130.78131, 131.48444, 132.18756, 132.89069, 133.59381, 134.29694, 135.00006, 135.70319, 136.40631, 137.10944, 137.81256, 138.51569, 139.21881, 139.92194, 140.62506, 141.32819, 142.03131, 142.73444, 143.43756, 144.14069, 144.84381, 145.54694, 146.25006, 146.95319, 147.65631, 148.35944, 149.06256, 149.76569, 150.46881, 151.17194, 151.87506, 152.57819, 153.28131, 153.98444, 154.68756, 155.39069, 156.09381, 156.79694, 157.50006, 158.20319, 158.90631, 159.60944, 160.31256, 161.01569, 161.71881, 162.42195, 163.12508, 163.8282, 164.53133, 165.23445, 165.93758, 166.6407, 167.34383, 168.04695, 168.75008, 169.4532, 170.15633, 170.85945, 171.56258, 172.2657, 172.96883, 173.67195, 174.37508, 175.0782, 175.78133, 176.48445, 177.18758, 177.8907, 178.59383, 179.29695, 180.00008, 180.7032, 181.40633, 182.10945, 182.81258, 183.5157, 184.21883, 184.92195, 185.62508, 186.3282, 187.03133, 187.73445, 188.43758, 189.1407, 189.84383, 190.54695, 191.25008, 191.9532, 192.65633, 193.35945, 194.06258, 194.7657, 195.46883, 196.17195, 196.87508, 197.5782, 198.28134, 198.98447, 199.68759, 200.39072, 201.09384, 201.79697, 202.50009, 203.20322, 203.90634, 204.60947, 205.31259, 206.01572, 206.71884, 207.42197, 208.12509, 208.82822, 209.53134, 210.23447, 210.93759, 211.64072, 212.34384, 213.04697, 213.75009, 214.45322, 215.15634, 215.85947, 216.56259, 217.26572, 217.96884, 218.67197, 219.37509, 220.07822, 220.78134, 221.48447, 222.18759, 222.89072, 223.59384, 224.29697, 225.00009, 225.70322, 226.40634, 227.10947, 227.81259, 228.51572, 229.21884, 229.92197, 230.62509, 231.32822, 232.03134, 232.73447, 233.43759, 234.14073, 234.84386, 235.54698, 236.2501, 236.95323, 237.65636, 238.35948, 239.0626, 239.76573, 240.46886, 241.17198, 241.8751, 242.57823, 243.28136, 243.98448, 244.6876, 245.39073, 246.09386, 246.79698, 247.5001, 248.20323, 248.90636, 249.60948, 250.3126, 251.01573, 251.71886, 252.42198, 253.1251, 253.82823, 254.53136, 255.23448, 255.9376, 256.64075, 257.34387, 258.047, 258.75012, 259.45325, 260.15637, 260.8595, 261.56262, 262.26575, 262.96887, 263.672, 264.37512, 265.07825, 265.78137, 266.4845, 267.18762, 267.89075, 268.59387, 269.297, 270.00012, 270.70325, 271.40637, 272.1095, 272.81262, 273.51575, 274.21887, 274.922, 275.62512, 276.32825, 277.03137, 277.7345, 278.43762, 279.14075, 279.84387, 280.547, 281.25012, 281.95325, 282.65637, 283.3595, 284.06262, 284.76575, 285.46887, 286.172, 286.87512, 287.57825, 288.28137, 288.9845, 289.68762, 290.39075, 291.09387, 291.797, 292.50012, 293.20325, 293.90637, 294.6095, 295.31262, 296.01575, 296.71887, 297.422, 298.12512, 298.82825, 299.53137, 300.2345, 300.93762, 301.64075, 302.34387, 303.047, 303.75012, 304.45325, 305.15637, 305.8595, 306.56262, 307.26575, 307.96887, 308.672, 309.37512, 310.07825, 310.78137, 311.4845, 312.18762, 312.89075, 313.59387, 314.297, 315.00012, 315.70325, 316.40637, 317.1095, 317.81262, 318.51575, 319.21887, 319.922, 320.62512, 321.32825, 322.03137, 322.7345, 323.43762, 324.14078, 324.8439, 325.54703, 326.25015, 326.95328, 327.6564, 328.35953, 329.06265, 329.76578, 330.4689, 331.17203, 331.87515, 332.57828, 333.2814, 333.98453, 334.68765, 335.39078, 336.0939, 336.79703, 337.50015, 338.20328, 338.9064, 339.60953, 340.31265, 341.01578, 341.7189, 342.42203, 343.12515, 343.82828, 344.5314, 345.23453, 345.93765, 346.64078, 347.3439, 348.04703, 348.75015, 349.45328, 350.1564, 350.85953, 351.56265, 352.26578, 352.9689, 353.67203, 354.37515, 355.07828, 355.7814, 356.48453, 357.18765, 357.89078, 358.5939, 359.29703]



class TemporalCoverage(OPeNDAPVariableCoverage):

    def __init__(self,openDAPRequestObject,atmosVariable):
        self.openDAPRequestObject = openDAPRequestObject
        self.openDAPNameSpace = openDAPRequestObject.get_opendap_namespace()
        self.atmosVariable = atmosVariable
        self.url = openDAPRequestObject.get_URL()
        self.url =self.url + ".ddx"

# My attempt at the Visitor Pattern. AtmosCoverage "visits" TemporalCoverage        
    def accept_time_variable(self,atmosCoverage):
        self.timeVariable = atmosCoverage.getTimeCoordinateForOPeNDAPVariable(self.atmosVariable)
    #Precondition for invoking getStartDate
    #self.timeVariable must be defined
    def getStartDate(self,atmosCoverage):
        tree = atmosCoverage.get_opendapxmltree()
        array = tree.findall(self.openDAPNameSpace+"Array")
        for el in array:
            name = el.get("name")
            if name == self.timeVariable:
                attr = el.findall(self.openDAPNameSpace+"Attribute")
                for child in attr:
                    if child.get("name") == "units":
                        val = child.find(self.openDAPNameSpace+"value")
                        timeD = val.text
                        p1 = re.sub(r'^Hour since ',"",timeD)
                        p2 = re.sub(r'T'," ",p1)
                        p3 = re.sub(r'Z$',"",p2)
                        p4 = p3.split("-")
                        #                print(p4)
                        year = p4[0]
                        month = p4[1]
                        p5 = p4[-1].split(" ")
                        day = p5[0]
                        #                print(p5)
                        hour = p5[1]
                        hour = hour.split(":")
                        hour = hour[0]
                        self.startDate = datetime(int(year),int(month),int(day),int(hour))
                        return self.startDate

    def getEndDate(self,atmosCoverage):
        tree = atmosCoverage.get_opendapxmltree()
        array = tree.findall(self.openDAPNameSpace+"Array")
        for el in array:
#            print(el.get("name"))
            name = el.get("name")
            if name == self.timeVariable:
                attr = el.find(self.openDAPNameSpace+"dimension")
                endDate = int(attr.get("size"))
                self.endDate = endDate
                return self.endDate
            
    def getTimeConstraint(self):
        pass

    def isLowerBoundary(self):
        pass
        
    def isUpperBoundary(self):
        pass

class ERA1TemporalCoverage(TemporalCoverage):

    def __init__(self,openDAPRequest,atmosVariable):
        super(ERA1TemporalCoverage,self).__init__(openDAPRequest,atmosVariable)
        self.time_span = openDAPRequest.get_time_span()
        self.year1 = int(self.time_span.get_year1())
        self.month1 = int(self.time_span.get_month1())
        self.day1 = int(self.time_span.get_day1())
        self.time1 = int(self.time_span.get_time1())
    
    def isLowerBoundary(self,atmosCoverage):
        self.date_start = super(ERA1TemporalCoverage,self).getStartDate(atmosCoverage)
        date_input = datetime(self.year1,self.month1,self.day1,self.time1)
        if (date_input < self.date_start):
            raise ValueError("Lower Bound of Data Set Is Reached")
        
    def isUpperBoundary(self,atmosCoverage):

        date_input = datetime(self.year1,self.month1,self.day1,self.time1)
        
        timeCurrentVal = super(ERA1TemporalCoverage,self).getEndDate(atmosCoverage)
        timeCurrentVal = int(timeCurrentVal)
        timeCurrentVal = (timeCurrentVal-1)*6
        before = self.date_start
        after = date_input
        hours_input = (after-before)//timedelta(seconds=3600)

        #        print(hours_input,timeCurrentVal)
        if (hours_input > timeCurrentVal):
            raise ValueError("Upper Bound of Data Set Is Reached")

        
    def getTimeConstraint(self): 
        date_start = self.date_start
        date_end = datetime(self.year1,self.month1,self.day1,self.time1)
        hours = (date_end - date_start)//timedelta(seconds=3600)
        hours = hours//6
        hours = hours -1
        self.timeIndex = "[" + str(hours) + ":1:" + str(hours) + "]"
        return {"time":self.timeVariable,"timeConstraint":self.timeIndex}


class ERA5TemporalCoverage(TemporalCoverage):

    def __init__(self,openDAPRequest,atmosVariable):
        super(ERA5TemporalCoverage,self).__init__(openDAPRequest,atmosVariable)
        self.time_span = openDAPRequest.get_time_span()
        self.year1 = int(self.time_span.get_year1())
        self.month1 = int(self.time_span.get_month1())
        self.day1 = int(self.time_span.get_day1())
        self.time1 = int(self.time_span.get_time1())
    
    def isLowerBoundary(self,atmosCoverage):
        self.date_start = super(ERA5TemporalCoverage,self).getStartDate(atmosCoverage)
        date_input = datetime(self.year1,self.month1,self.day1,self.time1)
        if (date_input < self.date_start):
            raise ValueError("Lower Bound of Data Set Is Reached")
        
    def isUpperBoundary(self,atmosCoverage):

        date_input = datetime(self.year1,self.month1,self.day1,self.time1)
        
        timeCurrentVal = super(ERA5TemporalCoverage,self).getEndDate(atmosCoverage)
        timeCurrentVal = int(timeCurrentVal)
        timeCurrentVal = (timeCurrentVal-1)*6
        before = self.date_start
        after = date_input
        hours_input = (after-before)//timedelta(seconds=3600)
#        print(hours_input,timeCurrentVal)
        if (hours_input > timeCurrentVal):
            raise ValueError("Upper Bound of Data Set Is Reached")

        
    def getTimeConstraint(self): 
        date_start = self.date_start
        date_end = datetime(self.year1,self.month1,self.day1,self.time1)
        hours = (date_end - date_start)//timedelta(seconds=3600)
        hours = hours//6
        hours = hours -1
        self.timeIndex = "[" + str(hours) + ":1:" + str(hours) + "]"
        return {"time":self.timeVariable,"timeConstraint":self.timeIndex}


class GFS025TemporalCoverage(TemporalCoverage):

    def __init__(self,openDAPRequestObject,atmosVariable):
        super(GFS025TemporalCoverage,self).__init__(openDAPRequest,atmosVariable)
        self.time_span = self.openDAPRequestObject.get_time_span()
        self.year1 = int(self.time_span.get_year1())
        self.month1 = int(self.time_span.get_month1())
        self.day1 = int(self.time_span.get_day1())
        self.time1 = int(self.time_span.get_time1())

    def isLowerBoundary(self,atmosCoverage):
        date_input = datetime(self.year1,self.month1,self.day1,self.time1)
        self.date_start = super(GFS025TemporalCoverage,self).getStartDate(atmosCoverage)
        if (date_input < self.date_start):
            print("Lower Bound of Data Set Is Reached")
            raise ValueError("Lower Bound of Data Set is Reached")
        
    def isUpperBoundary(self,atmosCoverage):

        date_input = datetime(self.year1,self.month1,self.day1,self.time1)
        timeCurrentVal = super(GFS025TemporalCoverage,self).getEndDate(atmosCoverage)
        timeCurrentVal = int(timeCurrentVal)
# Why 93 ? GFS provides data as follows
# The first time is analysis followed by 80 forecast intervals of three hours
# upto 240 hours ahead and then every 12 hours till 384 hours
        timeCurrentVal = timeCurrentVal/93
        timeCurrentVal = (timeCurrentVal-1)*6
        before = self.date_start
        after = date_input
        hours_input = (after-before)//timedelta(seconds=3600)
        if (hours_input > timeCurrentVal):
            print("Upper Bound of Data Set Is Reached")
            raise ValueError("Upper Bound of Data Set Is Reached")

    def getTimeConstraint(self): 
        date_start = self.date_start
        date_end = datetime(self.year1,self.month1,self.day1,self.time1)
        isAnalysis = self.openDAPRequestObject.isAnalysis()
        if isAnalysis is False:
            forecastTimestep = self.openDAPRequestObject.getForecastTimeStep()
        hours = (date_end - date_start)//timedelta(seconds=3600)
        hours = hours//6
        hours = hours -1
        hours = hours + forecastTimeStep
        timeIndex = "[" + str(hours) + ":1:" + str(hours) + "]"
        return {"time":self.timeVariable,"timeConstraint":self.timeIndex}

class UCAR3TemporalCoverage(TemporalCoverage):

    def __init__(self,openDAPRequest,atmosVariable):
        super(UCAR3TemporalCoverage,self).__init__(openDAPRequest,atmosVariable)
        self.time_span = openDAPRequest.get_time_span()
        self.year1 = int(self.time_span.get_year1())
        self.month1 = int(self.time_span.get_month1())
        self.day1 = int(self.time_span.get_day1())
        self.time1 = int(self.time_span.get_time1())
        
    def isLowerBoundary(self,atmosCoverage):
        date_input = datetime(self.year1,self.month1,self.day1,self.time1)
        self.date_start = super(UCAR3TemporalCoverage,self).getStartDate(atmosCoverage)
        if (date_input < self.date_start):
            print("Lower Bound of Data Set Is Reached")
            raise ValueError("Lower Bound of Data Set is Reached")
        
    def isUpperBoundary(self,atmosCoverage):

        date_input = datetime(self.year1,self.month1,self.day1,self.time1)
        timeCurrentVal = super(UCAR3TemporalCoverage,self).getEndDate(atmosCoverage)
        timeCurrentVal = int(timeCurrentVal)
# Why 4 ? UCAR provides data as follows
# The first time is analysis followed by 3 forecast intervals of three hours
# upto 9 hours
        timeCurrentVal = timeCurrentVal/4
        timeCurrentVal = (timeCurrentVal-1)*6
        before = self.date_start
        after = date_input
        hours_input = (after-before)//timedelta(seconds=3600)
        if (hours_input > timeCurrentVal):
            raise ValueError("Upper Bound of Data Set Is Reached")

        
    def getTimeConstraint(self): 
        date_start = self.date_start
        date_end = datetime(self.year1,self.month1,self.day1,self.time1)
        isAnalysis = self.openDAPRequestObject.isAnalysis()
        if isAnalysis is False:
            forecastTimestep = self.openDAPRequestObject.getForecastTimeStep()
            hours = (date_end - date_start)//timedelta(seconds=3600)
            hours = hours//6
            hours = hours -1
            hours = hours + forecastTimestep
        else:
            hours = (date_end - date_start)//timedelta(seconds=3600)
            hours = hours//6
            hours = hours -1
        self.timeIndex = "[" + str(hours) + ":1:" + str(hours) + "]"
        return {"time":self.timeVariable,"timeConstraint":self.timeIndex}

    
class UCAR2TemporalCoverage(TemporalCoverage):

    def __init__(self,openDAPRequest,atmosVariable):
        super(UCAR2TemporalCoverage,self).__init__(openDAPRequest,atmosVariable)
        self.time_span = openDAPRequest.get_time_span()
        self.year1 = int(self.time_span.get_year1())
        self.month1 = int(self.time_span.get_month1())
        self.day1 = int(self.time_span.get_day1())
        self.time1 = int(self.time_span.get_time1())
    
    def isLowerBoundary(self,atmosCoverage):
        self.date_start = super(UCAR2TemporalCoverage,self).getStartDate(atmosCoverage)
        date_input = datetime(self.year1,self.month1,self.day1,self.time1)
        if (date_input < self.date_start):
            raise ValueError("Lower Bound of Data Set Is Reached")
        
    def isUpperBoundary(self,atmosCoverage):

        date_input = datetime(self.year1,self.month1,self.day1,self.time1)
        
        timeCurrentVal = super(UCAR2TemporalCoverage,self).getEndDate(atmosCoverage)
        timeCurrentVal = int(timeCurrentVal)
        timeCurrentVal = (timeCurrentVal-1)*6
        before = self.date_start
        after = date_input
        hours_input = (after-before)//timedelta(seconds=3600)
#        print(hours_input,timeCurrentVal)
        if (hours_input > timeCurrentVal):
            raise ValueError("Upper Bound of Data Set Is Reached")

        
    def getTimeConstraint(self): 
        date_start = self.date_start
        date_end = datetime(self.year1,self.month1,self.day1,self.time1)
        hours = (date_end - date_start)//timedelta(seconds=3600)
        hours = hours//6
        hours = hours -1
        self.timeIndex = "[" + str(hours) + ":1:" + str(hours) + "]"
        return {"time":self.timeVariable,"timeConstraint":self.timeIndex}


    
class UCAR1TemporalCoverage(TemporalCoverage):

    def __init__(self,openDAPRequest,atmosVariable):
        super(UCAR1TemporalCoverage,self).__init__(openDAPRequest,atmosVariable)
        self.time_span = openDAPRequest.get_time_span()
        self.year1 = int(self.time_span.get_year1())
        self.month1 = int(self.time_span.get_month1())
        self.day1 = int(self.time_span.get_day1())
        self.time1 = int(self.time_span.get_time1())

    def isLowerBoundary(self,atmosCoverage):

        date_input = datetime(self.year1,self.month1,self.day1,self.time1)
        self.date_start = super(UCAR1TemporalCoverage,self).getStartDate(atmosCoverage)
        if (date_input < self.date_start):
            raise ValueError("Lower Bound of Data Set Is Reached")
        
    def isUpperBoundary(self,atmosCoverage):

        date_input = datetime(self.year1,self.month1,self.day1,self.time1)
        timeCurrentVal = super(UCAR1TemporalCoverage,self).getEndDate(atmosCoverage)
        timeCurrentVal = int(timeCurrentVal)
        timeCurrentVal = (timeCurrentVal-1)*6
        before = self.startDate
        after = date_input
        hours_input = (after-before)//timedelta(seconds=3600)
        if (hours_input > timeCurrentVal):
            raise ValueError("Upper Bound of Data Set Is Reached")

        
    def getTimeConstraint(self): 

        date_start = self.date_start
        date_end = datetime(self.year1,self.month1,self.day1,self.time1)
        hours = (date_end - date_start)//timedelta(seconds=3600)
        hours = hours//6
        hours = hours -1
        self.timeIndex = "[" + str(hours) + ":1:" + str(hours) + "]"
        return {"time":self.timeVariable,"timeConstraint":self.timeIndex}

class VerticalCoverage(OPeNDAPVariableCoverage):

    def __init__(self,openDAPRequest,atmosVariable):
        self.openDAPRequestObject = openDAPRequest
        self.openDAPNameSpace = self.openDAPRequestObject.get_opendap_namespace()
        self.atmosVariable = atmosVariable
        self.url = self.openDAPRequestObject.get_URL()
        self.info = netrc.netrc().hosts
        for key,value in self.info.items():
            self.username=value[0]
            self.password=value[2]
            
    def accept_isobaric_variable(self,atmosCoverage):
        self.isobaricVariable = atmosCoverage.getIsobaricVariableForAtmosVariable(self.atmosVariable)
    def get_isobaric_variable(self):
        return self.isobaricVariable
        
    def set_allowed_pressure_levels(self):
        url = self.url +".ascii?"+ self.isobaricVariable
        response = requests.get(url,verify=False,auth=(self.username,self.password))
        p1 = re.sub(r'^Dataset\s\{\s',"",response.text)
        reg_ex1 = r'^\s+Float32\s' + re.escape(self.isobaricVariable) + r'\['+re.escape(self.isobaricVariable)+r'\s=\s[0-9]+\]\;'
        p2 = re.sub(reg_ex1,"",p1)
        p3 = re.sub(r'\}\s[a-z]+(\/g|\/e)\/ds[0-9]+\.[0-9]\/[0-9]\/TP;',"",p2)
        p4 = re.sub(r'\-+',"",p3)
        reg_ex2 = re.escape(self.isobaricVariable) + r'\[[0-9]+\]'
        p5 = re.sub(reg_ex2,"",p4)
        p6 = re.sub(r'^\n\n\n\n',"",p5)
        p7 = re.sub(r'\n\n$',"",p6)
        preL = p7.split(",")
        self.pressureLevels = []
        for pl in preL:
            j = pl.replace(' ','')
            j = float(j)
            self.pressureLevels.append(j)            

    def get_allowed_pressure_levels(self):
#        print(self.pressureLevels)
        return self.pressureLevels
        
    def pressureLevelIndex(self,pressure):
        pressureLevels = self.get_allowed_pressure_levels()
        pressureIndex = None
#        print(pressure)
#        print(pressureLevels)
        if pressure in pressureLevels:
            pressureIndex = pressureLevels.index(pressure)
        return pressureIndex

        
class UCARConstraintExpressionGenerator:

        
    def getConstraintExpression(self,openDAPRequest,atmosVariable,pressureLevel):
        from OPeNDAPRequestObject import ERA1OPeNDAPRequest
        url = openDAPRequest.get_URL()
        url = url + ".grb2?"

        minLat = openDAPRequest.get_LatLonBox().get_north()
        maxLat = openDAPRequest.get_LatLonBox().get_south()
        minLon = openDAPRequest.get_LatLonBox().get_east()
        maxLon = openDAPRequest.get_LatLonBox().get_west()

        if isinstance(openDAPRequest,ERA1OPeNDAPRequest):
            spatialCoverage = ERA1SpatialCoverage()
        else:
            spatialCoverage = openDAPRequest.getSpatialCoverage()
        latConstraint = self.getLatConstraint(spatialCoverage,minLat,maxLat)

        lonConstraint = self.getLonConstraint(spatialCoverage,minLon,maxLon)

        isobaricVariable = openDAPRequest.getVerticalCoverage(atmosVariable).get_isobaric_variable()
#        print(isobaricVariable,atmosVariable)
        levelConstraint = self.getLevelConstraint(openDAPRequest.getVerticalCoverage(atmosVariable),pressureLevel)
        
        dict = openDAPRequest.getTemporalCoverage(atmosVariable).getTimeConstraint()

        timeConstraintVariable = dict["time"]

        timeIndex = dict["timeConstraint"]
        urlVariable1 =  "lat" + latConstraint
        urlVariable2 =  "lon" + lonConstraint
        urlVariable3=  isobaricVariable + levelConstraint
        urlTimeIndex =  timeConstraintVariable+ timeIndex
        urlAtmosVar =    atmosVariable

        url_final = url + urlVariable1 + ","+urlVariable2 + ","+urlTimeIndex +"," +urlVariable3 + ","+ urlAtmosVar + timeIndex + levelConstraint + latConstraint + lonConstraint
#        print(url_final)
        outputFileName = self.createOutputFileName(openDAPRequest,atmosVariable,pressureLevel)
        return {"url":url_final,"fileName":outputFileName}

    def getSurfaceConstraintExpression(self,openDAPRequest,surfaceVariable):

        from OPeNDAPRequestObject import ERA1OPeNDAPRequest

        url = openDAPRequest.get_URLSurface()
        url = url + ".grb2?"

        minLat = openDAPRequest.get_LatLonBox().get_north()
        maxLat = openDAPRequest.get_LatLonBox().get_south()
        minLon = openDAPRequest.get_LatLonBox().get_east()
        maxLon = openDAPRequest.get_LatLonBox().get_west()

        if isinstance(openDAPRequest,ERA1OPeNDAPRequest):
            spatialCoverage = ERA1SpatialCoverage()
        else:
            spatialCoverage = openDAPRequest.getSpatialCoverage()

        latConstraint = self.getLatConstraint(spatialCoverage,minLat,maxLat)

        lonConstraint = self.getLonConstraint(spatialCoverage,minLon,maxLon)

        dict = openDAPRequest.getTemporalCoverage(surfaceVariable).getTimeConstraint()
        timeConstraintVariable = dict["time"]
        timeIndex = dict["timeConstraint"]
        urlVariable1 =  "lat" + latConstraint
        urlVariable2 =  "lon" + lonConstraint
        urlTimeIndex =  timeConstraintVariable+ timeIndex
        urlSurfaceVar =    surfaceVariable

        url_final = url + urlVariable1 + ","+urlVariable2 + ","+urlTimeIndex + ","+ urlSurfaceVar + timeIndex + latConstraint + lonConstraint
#        print(url_final)
        outputFileName = self.createOutputFileNameSurface(openDAPRequest,surfaceVariable)
        return {"url":url_final,"fileName":outputFileName}

    def getLevelConstraint(self,verticalCoverage,pressureLevel):
        pressureLevelIndexMin = verticalCoverage.pressureLevelIndex(pressureLevel)
        pressureLevelIndexMax = pressureLevelIndexMin
            
        self.levelConstraint = "[" + str(pressureLevelIndexMin) +":1:"+str(pressureLevelIndexMax) + "]"
        return self.levelConstraint
    
    def getLatConstraint(self,spatialCoverage,minLat,maxLat):
        try:
            minLatIndex = spatialCoverage.getLatIndex(minLat)
        except:
            pass
            
        try:
            maxLatIndex = spatialCoverage.getLatIndex(maxLat)
        except:
            pass
        if (maxLatIndex >  minLatIndex):
            #Adjust for southern hemisphere latitudes as well
            #By switching
            #Always go from North to South(Indices must increase)
            copyV = minLatIndex
            minLatIndex = maxLatIndex
            maxLatIndex = copyV
        latConstraint = "[" + str(maxLatIndex) + ":" + "1" + ":" + str(minLatIndex) + "]"
        return latConstraint

    def getLonConstraint(self,spatialCoverage,minLon,maxLon):
        try:
            minLonIndex = spatialCoverage.getLonIndex(minLon)
        except:
            pass
        try:
            maxLonIndex = spatialCoverage.getLonIndex(maxLon)
        except:
            pass
        if (minLonIndex > maxLonIndex):
            copyV = minLonIndex
            minLonIndex = maxLonIndex
            maxLonIndex = copyV
        
        lonConstraint = "[" + str(minLonIndex) + ":" + "1" + ":" + str(maxLonIndex) + "]"
        return lonConstraint
    
    def createOutputFileName(self,openDAPRequestObject,atmosphericVariable,pressureLevel):
        time_span = openDAPRequestObject.get_time_span()
        year1 = time_span.get_year1()
        month1 = time_span.get_month1()
        day1 = time_span.get_day1()
        time1 = time_span.get_time1()
        outputFileName = atmosphericVariable +  "_" + str(int(pressureLevel))+"_"+str(year1) + "_" + str(day1) + "_" + str(month1) + "_" + str(time1) + "Z" + ".nc"
        return outputFileName

    def createOutputFileNameSurface(self,openDAPRequestObject,surfaceVariable):
        time_span = openDAPRequestObject.get_time_span()
        year1 = time_span.get_year1()
        month1 = time_span.get_month1()
        day1 = time_span.get_day1()
        time1 = time_span.get_time1()
        outputFileName = surfaceVariable +  "_" +str(year1) + "_" + str(day1) + "_" + str(month1) + "_" + str(time1) + "Z" + ".nc"
        return outputFileName
