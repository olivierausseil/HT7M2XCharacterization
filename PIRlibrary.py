#!/usr/bin/python2
import time
import RPi.GPIO as GPIO
from smbus2 import SMBus
bus = SMBus(1)

#GPIO initialization
ledPin = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(ledPin, GPIO.IN)

#variable
maxbyte = 65535 #maximum value to 2 bytes
detection = 0

def SetPIRparameters (sensitivityGain,  sensitivityTrigger, triggerTime ):
    #------- Sensitivity --------
    # in case argument has not been provided
    if None == sensitivityGain:
        sensitivityGain = int(16)
    else:
        int(sensitivityGain)

    # manage argument limits (0-31) because 5 bits allow (see datasheet_HT7Mx6 __ p12 _ 1. Sensor Config Register)
    if sensitivityGain < 0:
        sensitivityGain = 0

    if sensitivityGain > 31:
        sensitivityGain = 31

    # from there, sensitivity takes a value between 0 and 31 in all cases
    #print ("sensitivity Gain is: " + str(sensitivityGain) )



    if None == sensitivityTrigger:
        sensitivityTrigger = int(0)
    else:
        int(sensitivityTrigger)

    # manage argument limits (0-7) because 3 bits allow (see datasheet_HT7Mx6 __ p12 _ 1. Sensor Config Register)
    if sensitivityTrigger < 0:
        sensitivityTrigger = 0

    if sensitivityTrigger > 7:
        sensitivityTrigger = 7


    # from there, sensitivity takes a value between 0 and 7 in all cases
    #print ("sensitivity Trigger is: " + str(sensitivityTrigger) )

    # sum of the two sensitivity
    sensitivity = (sensitivityTrigger << 5) +  sensitivityGain

    if sensitivityTrigger == 0 :
        sensitivity = sensitivityGain
    if sensitivityGain == 0 :
        sensitivity = sensitivityTrigger
    #print sensitivity
    #-------------- end sensitivity ---------

    #---------------TriggerTime -------------
    if None == triggerTime:
        triggerTime = int(50)
    else:
        int(triggerTime)

    if triggerTime < 0:
        triggerTime = 0

    if triggerTime > maxbyte:
        triggerTime = maxbyte

    # cut in two the data
    triggerTimeMSB = triggerTime >> 8 # MSB
    triggerTimeLSB = triggerTime & 0xFF # LSB

    #triggerTime = int(triggerTime) * 10
    #----------------end TriggerTIme --------
    # -------------- end parser  ------------

    time.sleep(0.01)

    # change the trigger time of detection (see datasheet_HT7Mx6 __ p15 _ 3.Trig Time Interval )
    data_time = bus.read_i2c_block_data(0x4c, 3, 2)
    #print ( "data_time : " + str(data_time))
    data_time[1] = triggerTimeLSB
    data_time[0] = triggerTimeMSB

    #print ( "data_time change : " + str(data_time))
    bus.write_i2c_block_data(0x4c, 3, data_time)
    #print ( "trigger time  : " + str(data_time[1]))

    time.sleep(0.01)

    # change of trigger parameter (see datasheet_HT7Mx6 __ p12 _ 1. Sensor Config Register)

    data = bus.read_i2c_block_data(0x4c, 1, 2)
    data[1] = sensitivity
    bus.write_i2c_block_data(0x4c, 1, data)
    time.sleep(0.1)
    data = bus.read_i2c_block_data(0x4c, 1, 2)
    #print ( "sensitivity: " + str(data[1]))


def PIRdetection(timeout = 5):
    refTimeout = time.time()
    waitDetection = True
    flagTimeout = False
    while not flagTimeout and waitDetection:
        if GPIO.input(ledPin):
            if timeout <= time.time() - refTimeout:
                flagTimeout = True
        else :
            if waitDetection:
                print 'DETECTION'
                waitDetection = False

        time.sleep (0.001)

    if not waitDetection:
        return True
    else:
        if flagTimeout:
            return False

def PIRendDetection():

    if GPIO.input(ledPin):
        print 'END DETECTION'
        return True
    else:
        return False
