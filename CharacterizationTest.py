#!/usr/bin/python2

import time
import LoRaBench
import numpy as np
import argparse
import RPi.GPIO as GPIO
from log import logger

#GPIO initialization
ledPin = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(ledPin, GPIO.IN)

#recover the date and hour, choose the format to acquisition
#FORMAT = '%(asctime)s %(message)s',datefmt='%a %d %b %Y %H:%M:%S'
#logging.basicConfig(level = logging.INFO,
#                    format= '%(asctime)s %(message)s',
#                    datefmt='%a %d %b %Y %H:%M:%S')
#logging.Formatter.converter = time.gmtime


# variable initialization
maxword = 255
maxbyte = 65535
flagTime = 0
flagSendFrame = 0
timeDetection = 0
endTimeDetection = 0

# creation of PARSER : do argument when i launch the script
parser = argparse.ArgumentParser()
parser.add_argument('-SF', action='store', dest='spreadingFactor')
parser.add_argument('-PP', action='store', dest='power')
parser.add_argument('-FF', action='store', dest='frequencyOffset')
parser.add_argument('-NN', action='store', dest='numberOfPackets')
parser.add_argument('-LL', action='store', dest='lenghtOfPackets')
parser.add_argument('-DD', action='store', dest='delay')
results = parser.parse_args()

SendFrames = [0x04] #identification to SendFrames LoraBench datasheet

# SPREADING FACTOR -----------------------
if None == results.spreadingFactor:
    spreadingFactor = int(12) #default value
else:
    spreadingFactor = int(results.spreadingFactor,16)

# manage argument limits (0-255) (see datasheet_LoRaBench_160617_A05_FirmwareSpecification_EN __ p6 __ Command SendFrames)
if spreadingFactor < 0:
    spreadingFactor = 0

if spreadingFactor > maxword:
    spreadingFactor = maxword
SendFrames.append(spreadingFactor)

# POWER ------------------------------------------
if None == results.power:
    power = int(14) #default value
else:
    power = int(results.power,16)

# manage argument limits (0-255) (see datasheet_LoRaBench_160617_A05_FirmwareSpecification_EN __ p6 __ Command SendFrames)
if power < 0:
    power = 0

if power > maxword:
    power = maxword
SendFrames.append(power)

# FREQUENCY OFFSET -------------------------------------
if None == results.frequencyOffset:
    frequencyOffset = int(5100)
else:
    frequencyOffset = int(results.frequencyOffset,16)

if frequencyOffset < 0:
    frequencyOffset = 0

if frequencyOffset > maxbyte:
    frequencyOffset = maxbyte

# cut in two the data
SendFrames.append(frequencyOffset >> 8) # MSB
SendFrames.append(frequencyOffset & 0xFF) # LSB


# NUMBER OF PACKETS -------------------------------------
if None == results.numberOfPackets:
    numberOfPackets = int(1)
else:
    numberOfPackets = int(results.numberOfPackets,16)

if numberOfPackets < 0:
    numberOfPackets = 0

if numberOfPackets > maxbyte:
    numberOfPackets = maxbyte

# cut in two the data
SendFrames.append(numberOfPackets >> 8) # MSB
SendFrames.append(numberOfPackets & 0xFF) # LSB

# LENGHT OF PACKETS -------------------------------------
if None == results.lenghtOfPackets:
    lenghtOfPackets = int(10) #default value
else:
    lenghtOfPackets = int(results.lenghtOfPackets,16)

# manage argument limits (0-255) (see datasheet_LoRaBench_160617_A05_FirmwareSpecification_EN __ p6 __ Command SendFrames)
if lenghtOfPackets < 0:
    lenghtOfPackets = 0

if lenghtOfPackets > maxword:
    lenghtOfPackets = maxword

SendFrames.append(lenghtOfPackets)

# DELAY --------------------------------------------------
if None == results.delay:
    delay = int(32) #default value
else:
    delay = int(results.delay,16)

# manage argument limits (0-255) (see datasheet_LoRaBench_160617_A05_FirmwareSpecification_EN __ p6 __ Command SendFrames)
if delay < 0:
    delay = 0

if delay > maxword:
    delay = maxword

SendFrames.append(delay)

#print ( "Initial command frame: " + SendFrames)

# http://stackoverflow.com/questions/9448029/print-an-integer-array-as-hexadecimal-numbers
np.set_printoptions(formatter={'int':lambda x:hex(int(x))})
#np.set_printoptions(formatter={'int':hex})
#np.set_printoptions(formatter={'int': '{: 02x }'.format})
print ( "Initial command: " + str(np.array(SendFrames)))
#we go encode and create my frame to send
LoRaBench.LoRaBenchInit( )
a = LoRaBench.LoRaBenchSendFrame(SendFrames)
print ( "sendFrames: " + str(np.array(a)))

# check detection to the PIR and log date and time detection
detection = GPIO.input(ledPin)

while True:
    detectionTemporary = GPIO.input(ledPin)
    time.sleep(0.005)
    if detection == 0 :
        if detection != GPIO.input(ledPin):
            # change of state
            detection = GPIO.input(ledPin)
            timeDetection = time.time()
            logger.info('DETECTION ')
            print ''

    if detection != 0:
        if detection != GPIO.input(ledPin) :
            # change of state
            detection = GPIO.input(ledPin)
            endTimeDetection = time.time()
            logger.info('FIN DETECTION')
            print ''
            flagTime = 1


    if flagTime == 1 :
        flagTime = 0
        finalTime = endTimeDetection - timeDetection
        logger.info('detection time : %.2f ' %finalTime)
        print ''


    # analyse the answer of LoRaBench and if OK log date and time of end of transmission
    rxbuffer = LoRaBench.LoRaBenchReceiveFrame()

    # launch another cycle of emission
    if rxbuffer != 0 :
        if rxbuffer[0] == 0x80:
            time.sleep(5)
            print "--------------------------------------------------------------------------------------"
            print ( "sendFrames: " + str(np.array(SendFrames)))
            print ""
            LoRaBench.LoRaBenchSendFrame(SendFrames)
