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

    def reward(self, p_reward, size, delay_mean = 15, rate = 1 ):

#        p_reward        - Probability between 0 and 1 of getting reward
#        delay           - Delay, in sec, before getting reward
#        size            - Size of reward in ml
#        rate            - Rate of flow 1/sec
  
        #Setup the output pin for the reward to the Intan board
        GPIO.setup(12,GPIO.OUT)
        
        #Create an attribute for reward status 
        #so you can give it a value (On = reward Off = no reward)
        reward_status = 0 
        
        #Calculate the reward_delay based on the given parameters
        reward_delay = 1/rate * size
        
        #Calculate the delay based on the given parameters
        delay_ = np.random.exponential(delay_mean)
        time.sleep(delay_)
        
        if np.random.rand() < p_reward:
            
            
            #Turn on the water dispenser
            GPIO.output(self.pin, True)
            
            #You'll have to account for the time it
            #take for the water to get to the mouthpiece
            
            #Trigers output to Intan Board
            GPIO.output(12,True)
            
            #Control the size of the reward
            time.sleep(reward_delay)
            
            #Turn off the water dispenser
            GPIO.output(self.pin, False)
            
            #Stop the output to Intan Board
            GPIO.output(12,False)
            
            #Assign the current reward status
            reward_status ='ON'
            
        else:
            #Assign the current reward status
            reward_status ='OFF'
            
        
        return reward_status, delay_
    
    def pulse(self, duration = 0.001, rate = 20.0, train_length = 1):

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

#Set the name of the block of trials 
name = 'Test opto'


#Set your number of trials
num_trial = 2
#params = ['num_trial', 'opto_prob']
#params_defaults = [10, 0.5]
#
#for ind, param in enumerate(params):
#    try:
#        exec(param)
#    except NameError:
#        exec(param + ' = ' + str(params_default[ind]))
        
#Set probability for opto on
opto_prob = 1

#Set probability between 0 and 1 of getting reward
p_reward = .75

#Size of reward in ml
size = 2

#Save your trial parameters
with open('block_data.txt', 'w') as f:
    print('\n''Block_name:',name,
          '\n''Number of trials:',num_trial,
          '\n''The size of the reward in ml:',size,
          '\n''Probability of reward:',p_reward*100,'%',
          '\n''The opto probability:',opto_prob*100,'%', file=f)

#Assign a beginning value to trial_
trial_ = 0

#Assign a beginning value to trial_
ITI_ = 0 

#Create a list of Opto conditions
opto_cond = ['Opto_On','Opto_Off']

#Set the time for the beginning of the block
block_start = time.time()

while trial_ < num_trial:
    
    #Choose a opto condition from opto_cond array p = probability 
    #to get each entry in opto_cond
    opto_status_ = np.random.choice(opto_cond, p = [opto_prob, 1 - opto_prob])
    
    #Save the opto status
    with open('block_data.txt', 'a') as f:
        print('\n''Opto status:',opto_status_, file=f)
    
    #Set the time for the beginning of the trial
    trial_start = time.time()
    
    #Play the conditioned stimuli
    sound.play()
    GPIO.output(18,True)
    #maybe put a sleep statement
    GPIO.output(18,False)
    
    #Pause before the reward or opto
    time.sleep(3)

    if opto_status_ == 'Opto_Off' :

        #Give the reward
        reward_status, delay_ = water.reward(p_reward,size)
        with open('block_data.txt', 'a') as f:
            print('Reward Status:',reward_status, 
                  '\n''Delay:',np.around(delay_,2),file=f)

    else:

        #Do pulsetrain
        pulse_time, ipi  =  LED.pulse()
        #print'pulse length',np.around(np.array(pulse_time),5)
        

        #give the reward
        reward_status, delay_ = water.reward(p_reward,size)
        with open('block_data.txt', 'a') as f:
            print('Reward Status:',reward_status, 
                  '\n''Delay in sec:',np.around(delay_,2),file=f)

    #Calculate the trial length and add it to the list 
    trial_length = time.time() - trial_start

    
    #Return the length of the trial
    with open('block_data.txt', 'a') as f:
        print('Trial length in sec:',np.around(trial_length,2),file=f)
        
    #Count the number of trials
    trial_ += 1
    
    #Exit the loop if all trials have been completed
    if trial_ < num_trial:
        
        #Randomly give a ITI based on exp. distribution (mean_ITI)
        ITI_ = np.random.exponential(30)
        
        #Save the ITI 
        with open('block_data.txt', 'a') as f:
            print('Inter-trial Interval in sec:',np.around(ITI_,2),file=f)
        
        #Pause for the ITI before next trial 
        time.sleep(ITI_)


#Clean up the GPIOs
GPIO.cleanup()

#Calculate the length of the block of trials 
block_length = time.time()-block_start

#Return the length of the trial and the block
with open('block_data.txt', 'a') as f:
    print('\n''Block length in sec',np.around(block_length,2),file=f)
    


