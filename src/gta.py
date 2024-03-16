#!/usr/bin/env python3
##
# @mainpage Grand Theft API Project
#
# @section GTA Description
# Vehicle forensics tool for accessing vehicle data from manufacturers' REST API backends
#
# Copyright (c) 2023 Fachhochschule Münster. All rights reserved.
# @section Classes
# 
# Vehicle LogReqs ReqCreator Menu
# Manufacturer classes:
# Mercedes Bmw Audi Ford Hyundai Renault Dacia
#
import sys
import ReqCreator as RC
import Menu as menu
from Mercedes import Mercedes
from Bmw import Bmw
from Audi import Audi
from Ford import Ford
from Hyundai import Hyundai
from Renault import Renault
from Dacia import Dacia

## read whether user opted to use --verbose option or not
if(len(sys.argv)>1 and (sys.argv[1]=='--verbose' or sys.argv[1]=='-v')):
    VERBOSE = True
else:
    VERBOSE = False

## initialize each manufacturer instance by calling constructor and passing VERBOSE flag
mercedes = Mercedes(VERBOSE)
bmw = Bmw(VERBOSE)
audi = Audi(VERBOSE)
ford = Ford(VERBOSE)
hyundai = Hyundai(VERBOSE)
renault = Renault(VERBOSE)
dacia = Dacia(VERBOSE)

## main loop for the user to choose a manufacturer or exit the program
while True:
    menu.print_manufac()
    manufac = input("Choose manufacturer : ")
    if manufac == '0':
        exit(1)
    elif manufac == '1':
        mercedes = RC.mercedes_requests(mercedes)
    elif manufac == '2':
        bmw = RC.bmw_requests(bmw)
    elif manufac == '3':
        audi = RC.audi_requests(audi)
    elif manufac == '4':
        ford = RC.ford_requests(ford)
    elif manufac == '5':
        hyundai = RC.hyundai_requests(hyundai)
    elif manufac == '6':
        renault = RC.renault_request(renault)
    elif manufac == '7':
        dacia = RC.renault_request(dacia)
    else:
        print("unknown manufacturer")
