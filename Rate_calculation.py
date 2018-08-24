#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 22 09:31:07 2018

@author: jean-francoisboucher
"""
import time
import numpy as np
import RPi.GPIO as GPIO

#Setup the GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(25,GPIO.OUT)

#Collect a start time
start_time = time.time()


try:
    while True:
        GPIO.output(25,True)     # Turn on water
except KeyboardInterrupt:
    GPIO.output(25,False)  #Turn off water
    GPIO.cleanup()             
    length = time.time()-start_time #Calculate the length
    print('\n''The flow rate for your pump is',np.around((1/length),2),'ml/sec')

