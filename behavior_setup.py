#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 15 10:55:22 2018

@author: jean-francoisboucher
"""

import time
import RPi.GPIO as GPIO
import numpy as np
from pygame import mixer


GPIO.setwarnings(False)

mixer.init()

GPIO.setmode(GPIO.BCM)

class stim(object):

    def __init__(self,name,pin,io):
        self.name = name
        self.pin = pin
        self.io = io
        self.verbose = False
        self.GPIOsetup()

    def __str__(self):
        return'The {} {} associated to pin {}'.format(self.io,self.name,self.pin)

    def GPIOsetup (self):
        GPIO.setup(self.pin, self.io)

    def reward(self, p_reward = 1, delay_mean = 5, delay_sd = 0, size = 5):

#        p_reward        - Probability between 0 and 1 of getting reward
#        delay           - Delay, in sec, before getting reward
#        size            - Size of reward in sec

        delay_ = np.random.normal(loc = delay_mean, scale = delay_sd)
        time.sleep(delay_)
        
        if np.random.rand() < p_reward:
            GPIO.output(self.pin, True)
            time.sleep(size)
            GPIO.output(self.pin, False)


    def pulse(self, duration = 0.01, rate = 20.0, train_length = 1):

#        inputs:
#        --------------
#        duration       - Duration of pulse in sec
#        rate           - Rate of pulses in 1/sec
#        length         - Train length in sec


        start_time = time.time()
        train_length_curr = 0
        pulse_time = []
        ipi = []

        while train_length_curr < train_length:

            #Start and stop pulse for duration
            GPIO.output(self.pin, True)
            pulse_start = time.time()
            time.sleep(duration - (pulse_start - time.time()))
            GPIO.output(self.pin, False)

            #Calculate pulse time for this trial and save it
            pulse_time_rel_ =  time.time() - pulse_start
            pulse_time_abs_ = time.time()
            pulse_time = np.append(pulse_time, pulse_time_rel_)

            #Sleep for the appropriate time between pulses
            time.sleep(1/rate - (time.time() - pulse_start))

            #Update the current train length and append this trials'
            #ipi to the ipi vector
            train_length_curr = time.time() - start_time
            ipi = np.append(ipi, time.time() - (pulse_time_abs_))

        return pulse_time, ipi

#Configurate the sound
sound = mixer.Sound('beep-2.wav')

#Configurate the GPIOs
LED = stim("LED",23,GPIO.OUT)

water = stim("water",25,GPIO.OUT)

#Turn the opto On or Off
opto = True # False = no_opto True = opto

#Set you inter-trial intervals
ITI = 10

#Set your number of trials
num_trial = 3

#Do not modify those settings
trial = 0

trial_length = []

block_start = time.time()

while trial < num_trial:
    trial_start = time.time()
    #GPIO.output(24,True)
    sound.play()
    #GPIO.output(24,False)
    time.sleep(1)

    if opto is False :

        #give the reward

        #GPIO.output(16,True)

        water.reward()

        #GPIO.output(16,False)

    else:

        #Do pulsetrain
        #GPIO.output(12,True)

        pulse_time, ipi  =  LED.pulse()
        print('pulse length', pulse_time)
        #GPIO.output(12,False)


        #give the reward

        #GPIO.output(16,True)

        water.reward()

        #GPIO.output(16,False)

    trial += 1
    
    trial_length = np.append(trial_length, (time.time() - trial_start))
    
    if trial < num_trial:
        time.sleep(ITI)



GPIO.cleanup()

block_length = time.time()-block_start

print('Trial length', round(trial_length,2))
print('Block length', round(block_length,2))

