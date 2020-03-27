#!/usr/bin/python3.5


import sys 

import configparser

import subprocess

import shlex

import numpy as np

from datadownloader import UCARConstraintExpressionGenerator

from OPeNDAPRequestInputAssembler import OPeNDAPRequestInputAssembler

from OPeNDAPRequestObject import Reanalysis1OPeNDAPRequest

def validateOPeNDAPRequest(openDAPRequestObject):
    oria = OPeNDAPRequestInputAssembler(openDAPRequestObject)
    atmosVariables = openDAPRequestObject.get_atmos_variables()

    pressureLevels = openDAPRequestObject.get_pressure_levels()

    for index,val in enumerate(atmosVariables):
        atmosVariable = val
        oria.validateOPeNDAPRequestInput(atmosVariable,pressureLevels)

def validateSurfaceOPeNDAPRequest(openDAPRequestObject):
    oria = OPeNDAPRequestInputAssembler(openDAPRequestObject)
    surfaceVariables = openDAPRequestObject.get_surface_variables()
 
    for index,val in enumerate(surfaceVariables):
        surfaceVariable = val
        oria.validateSurfaceOPeNDAPRequestInput(surfaceVariable)

def createSuraceConstraintExpressions(openDAPRequestObject):
    constraintExpressionList = []
    surfaceVariables = openDAPRequestObject.get_surface_variables()
    for index,val in enumerate(surfaceVariables):
        surfaceVariable = val
        ucarConstraintExpressionGen = UCARConstraintExpressionGenerator()
        constraintExpression = ucarConstraintExpressionGen.getSurfaceConstraintExpression(openDAPRequestObject,surfaceVariable)
        constraintExpressionList.append(constraintExpression)

    return constraintExpressionList

        
def createConstraintExpressions(openDAPRequestObject):
    constraintExpressionList = []
    atmosVariables = openDAPRequestObject.get_atmos_variables()
    pressureLevels = openDAPRequestObject.get_pressure_levels()
    for index,val in enumerate(atmosVariables):
        atmosVariable = val
        for idx,pressure in enumerate(pressureLevels):
            ucarConstraintExpressionGen = UCARConstraintExpressionGenerator()
            constraintExpression = ucarConstraintExpressionGen.getConstraintExpression(openDAPRequestObject,atmosVariable,pressure)
            constraintExpressionList.append(constraintExpression)
            
    return constraintExpressionList

def executeDownload(openDAPRequestObject,constraintExpressionList):
    for i,dict in enumerate(constraintExpressionList):
        url = dict['url']
        outputFileName = dict['fileName']
        command_list = shlex.split('nccopy -k 4 '+url+' '+ outputFileName)
        subprocess.check_call(command_list)
                    

def executeSurfacePressureDownload(openDAPRequestObject):
    surfaceVariable = openDAPRequestObject.get_surface_variables()
    url=    createConstraintExpressionForSurfacePressure(surfaceVariable)
    outputFileName = createOutputFileName(openDAPRequestObject,surfaceVariable)
    command_list = shlex.split('nccopy -k 4 ' + url + ' '+ outputFile)
    subprocess.check_call(command_list)

def get_class( cls ):
    parts = cls.split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)            
    return m


def main():

    # Dynamic class loading/Abstract Factory
    config = configparser.ConfigParser()
    config.read('ucar.cfg')
    requestType = config.get('RequestType','requestType')
    print(requestType)

    openDAPNameSpace = config.get('RequestType','openDAPNameSpace')
    module,className = requestType.split('.',1)
    url = config.get(className,'url')
    urlSurface = config.get(className,'urlSurface')
    grid_spacing = config.get(className,'grid_spacing')
    module = get_class(requestType)
    openDAPRequestObject = module()
    #
    openDAPRequestObject.set_opendap_namespace(openDAPNameSpace)
    openDAPRequestObject.set_URL(url,grid_spacing)
    if urlSurface:
        openDAPRequestObject.set_surfaceURL(urlSurface,grid_spacing)
    year1 = int(config.get(className,'year1'))
    month1 = int(config.get(className,'month1'))
    day1  = int(config.get(className,'day1'))
    time1 =  config.get(className,'time1')

    isAnalysis = bool(config.get(className,'isAnalysis'))
    forecastTimestep = int(config.get(className,'forecastTimestep'))
    year2 = int(config.get(className,'year2'))
    month2 = int(config.get(className,'month2'))
    day2  = int(config.get(className,'day2'))
    time2 =  config.get(className,'time2')

    openDAPRequestObject.setAnalysisRequest(isAnalysis)
    openDAPRequestObject.setForecastTimestep(forecastTimestep)
    openDAPRequestObject.set_time_span(year1,month1,day1,time1,year2,month2,day2,time2)
    
    pressure = config.get(className,'pressureLevels')
    pL = pressure.split(",")

    pressureLevels = []
    for i,val in enumerate(pL):
        val = float(val)
        if isinstance(openDAPRequestObject,Reanalysis1OPeNDAPRequest):
            val1 = val//float(10)
            pressureLevels.append(val1)
        else:
            pressureLevels.append(val)
    openDAPRequestObject.set_PressureLevels(pressureLevels)
    atmos = config.get(className,'atmosVariables')
    atmosVariables = atmos.split(",")
    openDAPRequestObject.set_AtmosVariables(atmosVariables)

    #   print(atmosVariables)

    surfaceVariable = config.get(className,'surfaceVariables')
    surfaceVariables = surfaceVariable.split(",")
    openDAPRequestObject.set_SurfaceVariables(surfaceVariables)
    minLat = float(config.get(className,'minLat'))
    maxLat = float(config.get(className,'maxLat'))
    minLon = float(config.get(className,'minLon'))
    maxLon = float(config.get(className,'maxLon'))
    
    minLon = np.mod(minLon,360)
    maxLon = np.mod(maxLon,360)

    openDAPRequestObject.set_LatLonBox(minLon,maxLon,minLat,maxLat)
    validateOPeNDAPRequest(openDAPRequestObject)
    constraintExpressionList = createConstraintExpressions(openDAPRequestObject)
    executeDownload(openDAPRequestObject,constraintExpressionList)


    validateSurfaceOPeNDAPRequest(openDAPRequestObject)
    constraintExpressionList = createSuraceConstraintExpressions(openDAPRequestObject)
    executeDownload(openDAPRequestObject,constraintExpressionList)

main() # Call the main function

