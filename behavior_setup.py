#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 15 10:55:22 2018

@author: jean-francoisboucher
"""
import datetime 
import time
import RPi.GPIO as GPIO
import numpy as np
from pygame import mixer
import sys, getopt
import pandas as pd

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
        self.GPIOsetup()

    def __str__(self):
        return'The {} {} associated to pin {}'.format(self.io,self.name,self.pin)

    def GPIOsetup (self):
        #Set up the GPIO pins you will be using as inputs or outputs
        GPIO.setup(self.pin, self.io)
        
    def triggerOn(self):
        #Trigger the TTL to start recording
        GPIO.output(self.pin,True)
    
    def triggerOff(self):
        #Stop the TTL to stop recording
        GPIO.output(self.pin,False)
        
    def reward(self, p_reward, size, delay_mean = 3, mn = 0.5,
               mx = 7, rate = 1 ):

#        p_reward        - Probability between 0 and 1 of getting reward
#        delay           - Delay, in sec, before getting reward
#        size            - Size of reward in ml
#        mn and mx       - Limits for the length of the delay
#        rate            - Rate of flow 1/sec
  
        #Setup the output pin for the reward to the Intan board
        GPIO.setup(12,GPIO.OUT)
        
        #Create an attribute for reward status 
        #so you can give it a value (On = reward Off = no reward)
        reward_status = 0 
        
        #Calculate the reward_delay based on the given parameters
        reward_delay = 1/rate * size
        
        #Calculate the delay based on the given parameters
        delay_ = np.around(np.random.exponential(delay_mean),2)
        
        #Make sure the delay is within the given min and max
        while delay_ < mn or delay_ > mx:
            delay_ = np.around(np.random.exponential(delay_mean),2)
        
        #Pause before giving the reward
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
    
    def sound(size):
        
        #Assign the sound command associated to large and small reward
        large = mixer.Sound('beep-3.wav')
        small = mixer.Sound('beep-2.wav')
        
        #Setup the output pin for the sound to the Intan board
        GPIO.setup(18,GPIO.OUT)
        
        if size >= 5:
            #TTl to intan board
            GPIO.output(18,True)
            
            #Play the conditioned stimuli
            large.play() 
            
            #TTL off 
            GPIO.output(18,False)
            
            #Pause before the reward or opto
            time.sleep(2)
            
        else:
            #TTl to intan board
            GPIO.output(18,True)
            
            #Play the conditioned stimuli
            small.play() 
            
            #TTL off 
            GPIO.output(18,False)
            
            #Pause before the reward or opto
            time.sleep(2)
        
    
    def params(argv):
        name = ''
        num_trial = ''
        opto_prob = ''
        size = ''
        p_reward = ''
       
        try:
            opts, args = getopt.getopt(argv,"hn:t:o:s:p:",["nam=","ntrial=",
                                                        "oprob=","siz=",
                                                        "prew="])
    
        except getopt.GetoptError:
            print('\n''behavior_setup.py -n <name> -t <num_trial>',
                  '-o <opto_prob> -s <size> -p <p_reward>''\n')
            sys.exit(2)
       
        for opt, arg in opts:
            if opt == '-h':
                print('\n''behavior_setup.py -n <name> -t <num_trial>', 
                      '-o <opto_prob> -s <size> -p <p_reward>''\n')
                sys.exit()
            elif opt in ("-n", "--nam"):
                name = arg
          
            elif opt in ("-t", "--ntrial"):
                num_trial = int(arg)
             
            elif opt in ("-o", "--oprob"):
                opto_prob = float(arg)
             
            elif opt in ("-s", "--siz"):
                size = float(arg)
             
            elif opt in ("-p", "--prew"):
                p_reward = float(arg)
                
        return name,num_trial,opto_prob,size,p_reward


#Assign GPIOs 
TTL = stim("TTL",16,GPIO.OUT)        

LED = stim("LED",23,GPIO.OUT)

water = stim("water",25,GPIO.OUT)

#Choose block paramenters
if __name__ == "__main__":
    name,num_trial,opto_prob,size,p_reward = stim.params(sys.argv[1:])
    
    print('\n''Name:', name)
       
    print('The number of trials:',num_trial)
       
    print('Probability of Opto is :',opto_prob*100,'%')
      
    print('The reward is',size,'ml')
       
    print('Probability of reward is',p_reward*100,'%')


#Ask for confirmation before beginning the block
confirmation = input('\n''Please confirm the chosen parameters (y/n):')
    
    
if confirmation == 'y':
    
    #Get today's date 
    now = datetime.datetime.now()
    
    #Save your trial parameters
    with open('block_data.txt', 'a') as f:
        print('\n',now.strftime('%Y-%m-%d %H:%M'),
              '\n''Block_name:',name,
              '\n''Number of trials:',num_trial,
              '\n''The size of the reward:',size,'ml',
              '\n''Probability of reward:',p_reward*100,'%',
              '\n''Probability of Opto stimulation:',opto_prob*100,'%', file=f)

    #Assign a beginning value to trial_
    trial_ = 0
    
    #Assign a beginning value to trial_
    ITI_ = 0 
    
    #Assign a max and min for ITI
    mn = 3
    mx = 25
    
    #Create a list of Opto conditions
    opto_cond = ['ON','OFF']
    
    #Create two empty data frame
    df1 = pd.DataFrame(index= None, columns =['Trial','ITI'])
    
   
    df2 = pd.DataFrame(index = None, columns =['Opto status','Reward status',
                                               'Delay','Trial length'])
    
    #Set the time for the beginning of the block
    block_start = time.time()
    
    #Start data recording on acq software
    TTL.triggerOn()
    
    while trial_ < num_trial:
        #Set the time for the beginning of the trial
        trial_start = time.time()
        
        #Append the current trial and ITI
        df1 = df1.append ({'Trial':trial_,'ITI':ITI_},
                          ignore_index=True)
        
        #Choose a opto condition from opto_cond array p = probability 
        #to get each entry in opto_cond
        opto_status_ = np.random.choice(opto_cond, p = [opto_prob, 1 - opto_prob])
        
        #Play the sound associated to the reward size
        stim.sound(size)
 

        if opto_status_ is 'OFF' :
    
            #Give the reward
            reward_status, delay_ = water.reward(p_reward,size)
    
        else:
    
            #Do pulsetrain
            pulse_time, ipi  =  LED.pulse()
            
    
            #give the reward
            reward_status, delay_ = water.reward(p_reward,size)

    
        #Calculate the trial length 
        trial_length = np.around(time.time() - trial_start,2)
    
        #Append all the current trial conditions to the data frame
        df2 = df2.append({'Opto status':opto_status_,
                        'Reward status':reward_status,
                        'Delay':delay_,
                        'Trial length':trial_length,},ignore_index=True)
            
        #Add to the trial counter
        trial_ += 1
        
        #Set if all trials have been completed before producing a new ITI
        if trial_ < num_trial:
            
            #Randomly give a ITI based on exp. distribution (mean_ITI)
            ITI_ = np.around(np.random.exponential(7),2)
            
            #Make sure the ITI is within the given min and max
            while ITI_ < mn or ITI_ > mx:
                ITI_ = np.around(np.random.exponential(7),2)
                            
        else:
            ITI_ = 0
        
        #Pause for the ITI before next trial 
        time.sleep(ITI_)
    
    
    #Calculate the length of the block of trials 
    block_length = np.around(time.time()-block_start,2)
    
    #Stop data recording on acq software
    TTL.triggerOff()
    
    #Join the two dataframe together
    df_final = pd.concat([df1, df2], axis=1)
     
    #Save to a csv file
    df_final.to_csv('Trial_data.csv',index=False)
    
    #Return the length of the trial and the block
    with open('block_data.txt', 'a') as f:
        print('Block length',block_length,'sec',file=f)
        
    
#Clean up the GPIOs
#GPIO.cleanup()

