#!/usr/bin/python3.6

import sys 

import os

import subprocess

import shlex

cmd = "rm  airFile.nc uwndFile.nc vwndFile.nc hgtFile.nc rhumFile.nc"

subprocess.call(cmd,shell=True)


#Begin merging humidity files
file_list = [ file for file in os.listdir('.') if file.startswith("rhum") ]

filePressureLevelDictionary = {}

for file in file_list:

    pressureLevel = int(file.split("_")[1])
    filePressureLevelDictionary[pressureLevel] = file

file = ""    

rhumFile = "rhumFile.nc"
for key in sorted(filePressureLevelDictionary,reverse=True):
    file =  file + " " +  filePressureLevelDictionary[key]


cmd = "cdo merge " + file + " " + rhumFile

subprocess.call(cmd,shell=True)



#Begin merging geopotential height files
file_list = [ file for file in os.listdir('.') if file.startswith("hgt") ]

filePressureLevelDictionary = {}

for file in file_list:

    pressureLevel = int(file.split("_")[1])
    filePressureLevelDictionary[pressureLevel] = file

file = ""    

outputFile = "hgtFile.nc"
for key in sorted(filePressureLevelDictionary,reverse=True):
    file =  file + " " +  filePressureLevelDictionary[key]


cmd = "cdo merge " + file + " " + outputFile

subprocess.call(cmd,shell=True)


#Begin merging air temperature files
file_list = [ file for file in os.listdir('.') if file.startswith("air") ]

filePressureLevelDictionary = {}

for file in file_list:

    pressureLevel = int(file.split("_")[1])
    filePressureLevelDictionary[pressureLevel] = file

file = ""    

outputFile2 = "airFile.nc"
for key in sorted(filePressureLevelDictionary,reverse=True):
    file =  file + " " +  filePressureLevelDictionary[key]


cmd = "cdo merge " + file + " " + outputFile2

subprocess.call(cmd,shell=True)


file_list = ["airFile.nc"]

#End merging air files


#Begin merging uwnd files


file_list = [ file for file in os.listdir('.') if file.startswith("uwnd") ]

filePressureLevelDictionary = {}

for file in file_list:
    pressureLevel = int(file.split("_")[1])
    filePressureLevelDictionary[pressureLevel] = file

file = ""    
outputFile3 = "uwndFile.nc"
for key in sorted(filePressureLevelDictionary,reverse=True):
    file =  file + " " +  filePressureLevelDictionary[key]

cmd = "cdo merge " + file + " " + outputFile3

subprocess.call(cmd,shell=True)

#End merging uwnd files

#Begin merging vwnd files

file_list = [ file for file in os.listdir('.') if file.startswith("vwnd") ]

filePressureLevelDictionary = {}

for file in file_list:
    pressureLevel = int(file.split("_")[1])
    filePressureLevelDictionary[pressureLevel] = file

file = ""    
outputFile4 = "vwndFile.nc"
for key in sorted(filePressureLevelDictionary,reverse=True):
    file =  file + " " +  filePressureLevelDictionary[key]

cmd = "cdo merge " + file + " " + outputFile4

subprocess.call(cmd,shell=True)

#End merging vwnd files

mergeFile = "PFile.nc"

cmd = "cdo merge "  + " " +outputFile+ " " + outputFile2 + " " + outputFile3 + " " + outputFile4  + " "  + mergeFile

subprocess.call(cmd,shell=True)


