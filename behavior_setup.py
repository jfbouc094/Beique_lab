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

#Turn off the GPIO warnings
GPIO.setwarnings(False)

#Initiate the module controlling the sound
mixer.init()

#Set the mode of the pins (broadcom vs local) 
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
        
        #Set up the GPIO pins you will be using as inputs or outputs
        GPIO.setup(self.pin, self.io)

    def reward(self, p_reward = .75, delay_mean = 5, delay_sd = 2, size = 5):

#        p_reward        - Probability between 0 and 1 of getting reward
#        delay           - Delay, in sec, before getting reward
#        size            - Size of reward in sec
  
        #Setup the output pin for the reward to the Intan board
        GPIO.setup(12,GPIO.OUT)
        
        #Start an empty list for reward status (On = reward Off = no reward)
        reward_status = []
        
        #Calculate the delay based on the given parameters
        delay_ = np.random.normal(loc = delay_mean, scale = delay_sd)
        time.sleep(delay_)
        
        if np.random.rand() < p_reward:
            
            #Save the current reward status
            reward_status.append('ON')
            
            #Trigers output to Intan Board
            GPIO.output(12,True)
            
            #Turn on the water dispenser
            GPIO.output(self.pin, True)
            
            #Control the size of the reward
            time.sleep(size)
            
            #Turn off the water dispenser
            GPIO.output(self.pin, False)
            
            #Stop the output to Intan Board
            GPIO.output(12,True)
            
        else:
            #Save the current reward status
            reward_status.append('OFF')
            
        
        return reward_status
    
    def pulse(self, duration = 0.01, rate = 20.0, train_length = 1):

#        inputs:
#        --------------
#        duration       - Duration of pulse in sec
#        rate           - Rate of pulses in 1/sec
#        length         - Train length in sec

        #Setup the output pin for the opto to the Intan board
        GPIO.setup(24,GPIO.OUT)
        
        start_time = time.time()
        train_length_curr = 0
        pulse_time = []
        ipi = []

        while train_length_curr < train_length:
            #Trigers output to Intan Board
            GPIO.output(24,True)
            
            #Start and stop pulse for duration
            GPIO.output(self.pin, True)
            pulse_start = time.time()
            time.sleep(duration - (pulse_start - time.time()))
            GPIO.output(self.pin, False)

            #Stop output to Intan Board
            GPIO.output(24,False)

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

#Assign the sound command
sound = mixer.Sound('beep-2.wav')

#Setup the output pin for the sound to the Intan board
GPIO.setup(18,GPIO.OUT)


#Assign GPIOs
LED = stim("LED",23,GPIO.OUT)

water = stim("water",25,GPIO.OUT)

#Turn the opto On or Off
opto = True # False = no_opto True = opto

#Set you inter-trial intervals
ITI = 5

#Set your number of trials
num_trial = 4

#Do not modify those settings
trial = 0

trial_length = []

block_start = time.time()

while trial < num_trial:
    #Set the time for the beginning of the trial
    trial_start = time.time()
    
    #Play the conditioned stimuli 
    GPIO.output(18,True)
    sound.play()
    GPIO.output(18,False)
    
    #Pause before the reward or opto
    time.sleep(3)

    if opto is False :

        #Give the reward
        reward_status = water.reward()
        print('Reward Status', reward_status)


    else:

        #Do pulsetrain
        pulse_time, ipi  =  LED.pulse()
        print('pulse length', (np.around(np.array(pulse_time),5)))
        

        #give the reward
        reward_status = water.reward()
        print('Reward Status', reward_status)

    #Counting the number of trials
    trial += 1
    
    #Calculate the trial length and add it to the list 
    trial_length = np.append(trial_length, (time.time() - trial_start))
    
    #Exit the loop if all trials have been completed
    if trial < num_trial:
        time.sleep(ITI)


#Clean up the GPIOs
GPIO.cleanup()

#Calculate the length of the block of trials 
block_length = time.time()-block_start

#Return the length of the trial and the block
print('Trial length', (np.around(np.array(trial_length),2)))
print('Block length', (np.around(block_length,2)))

