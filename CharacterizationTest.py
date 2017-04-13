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
nbmaxcpt = 1000000
flagDetectionOrNot = 0
CptCycle = 1


#log variable
timeDetection = 0
endTimeDetection = 0
startDetection = 0
stopDetection = 0

# creation of PARSER : do argument when i launch the script
parser = argparse.ArgumentParser()
parser.add_argument('-SF', action='store', dest='spreadingFactor')
parser.add_argument('-PP', action='store', dest='power')
parser.add_argument('-FF', action='store', dest='frequencyOffset')
parser.add_argument('-NN', action='store', dest='numberOfPackets')
parser.add_argument('-LL', action='store', dest='lenghtOfPackets')
parser.add_argument('-DD', action='store', dest='delay')
parser.add_argument('-CT', action='store', dest='cptmax')
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

#CPTMAX -------------------------------------------------
if None == results.cptmax:
    Cptmax = int(10) #default value
else:
    Cptmax = int(results.cptmax,16)

if Cptmax < 0:
    Cptmax = 0

if Cptmax > nbmaxcpt:
    Cptmax = nbmaxcpt

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
logger.info('Cycle ' + str (CptCycle))

#while CptCycle != Cptmax:
while True:
    time.sleep(0.001)

    #detection to the sensor PIR
    if detection == 0 :
        if detection != GPIO.input(ledPin):

            # log
            deltaTimeStart = time.time() - startDetection
            deltaTimeStart = round(deltaTimeStart,3)
            logger.info('deltaTimeStart ' + str (deltaTimeStart))

            # for indicate if we have a detection or not by the sensor when a frame is send by LoRaBench
            flagDetectionOrNot = 1

            # change of state
            detection = GPIO.input(ledPin)

    #detection to the sensor PIR
    if detection != 0:
        if detection != GPIO.input(ledPin) :

            #log
            stopDetection = time.time()

            # change of state
            detection = GPIO.input(ledPin)


    # analyse the answer of LoRaBench and if OK log date and time of end of transmission
    rxbuffer = LoRaBench.LoRaBenchReceiveFrame()

    # Check if the message inside buffer is the start TX answer or the stop TX answer
    # launch another cycle of emission
    if rxbuffer != 0 :
        if (rxbuffer[0] == 0x84 ):
            if (rxbuffer[1] == 0x00 ):
                #logger.info('start answer is ok')
                startDetection = time.time()
                #print 'start answer is ok'
            else:
                logger.info("error, the start answer is false : " + str(rxbuffer))
                print ''

        #check if is the answer of start
        if (rxbuffer[0] == 0x80 ):
            if (rxbuffer[1] == 0x04 ):
                # Can check if the sensor detect or not the frame send by LoRabench
                if flagDetectionOrNot == 1:
                    deltaTimeStop = time.time() - stopDetection
                    deltaTimeStop = round(deltaTimeStop,3)
                    logger.info('deltaTimeStop ' + str (deltaTimeStop))
                else:
                    logger.info('No detection during this cycle')
                #print 'stop answer is ok'
                print ''
            else:
                logger.info("error, the stop answer is false : " + str(rxbuffer))
                print ''

            flagDetectionOrNot = 0
            time.sleep(2)

            # we test the number of cycle in comparaison to the user ask
            if (CptCycle == Cptmax):
                print '-------------- THE END -------------------'
                break

            # a new cycle begin
            CptCycle += 1
            print ""
            print ""

            #log
            logger.info('Cycle ' + str (CptCycle))

            print "--------------------------------------------------------------------------------------"
            #print ( "sendFrames: " + str(np.array(SendFrames)))
            #print ""

            #launch a new send frame
            LoRaBench.LoRaBenchSendFrame(SendFrames)
