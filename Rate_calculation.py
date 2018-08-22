#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 22 09:31:07 2018

@author: jean-francoisboucher
"""
import time
import numpy as np

import RPi.GPIO as GPIO


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(23,GPIO.OUT)

start_time = time.time()

try:
    while True:
        GPIO.output(23,True)     # Turn on water
        print('Start')
except KeyboardInterrupt:
    print ("Done")
    GPIO.output(23,False)
    GPIO.cleanup()             
    length = time.time()-start_time
    print('Length', (np.around(length,2)))

