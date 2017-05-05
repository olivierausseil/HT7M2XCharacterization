#!/usr/bin/python2

import serial
import crcmod
import binascii
import time
import numpy as np
from log import logger
import json

maxword = 255
maxbyte = 65535
STX = 0x02
ETX = 0x03

json_file = 'testConfigFile.json'
json_data = open(json_file)
data = json.load(json_data)
json_data.close()

def RfInit():
    # initialization of serial
    global ser
    try:
        ser = serial.Serial(
            port='/dev/ttyUSB0',
            baudrate = 9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
            )
	#print ("Using USB0")
    except:
        ser = serial.Serial(
            port='/dev/ttyUSB1',
            baudrate = 9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
            )
	#print ("Using USB1")

def CreateFrame():
    header,spreadingFactor,power,frequencyOffset,numberOfPackets,lenghtOfPackets,delay = 0,0,0,0,0,0,0
    sendFrame = []
    for keys,value in data['frameToSend'].items():
        if keys == 'header':
            header = value
        if keys == 'spreadingFactor':
            spreadingFactor = value
            #print 'spreadingFactor',spreadingFactor
        if keys == 'power':
            power = value
            #print 'power',power
        if keys == 'frequencyOffset':
            frequencyOffset = value
            #print 'frequencyOffset',frequencyOffset
        if keys == 'numberOfPackets':
            numberOfPackets = value
            #print 'numberOfPackets',numberOfPackets
        if keys == 'lenghtOfPackets':
            lenghtOfPackets = value
            #print 'lenghtOfPackets',lenghtOfPackets
        if keys == 'delay':
            delay = value
            #print 'delay',delay"""


    sendFrame.append(header)
    # SPREADING FACTOR -----------------------
    if spreadingFactor == 0:
        spreadingFactor = int(12) #default value
    else:
        spreadingFactor

    # manage argument limits (0-255) (see datasheet_LoRaBench_160617_A05_FirmwareSpecification_EN __ p6 __ Command sendFrames)
    if spreadingFactor < 0:
        spreadingFactor = 0

    if spreadingFactor > maxword:
        spreadingFactor = maxword
    #print 'spreadingFactor',spreadingFactor
    sendFrame.append(spreadingFactor)

    # POWER ------------------------------------------
    if power == 0:
        power = int(14) #default value
    else:
        power

    # manage argument limits (0-255) (see datasheet_LoRaBench_160617_A05_FirmwareSpecification_EN __ p6 __ Command sendFrames)
    if power < 0:
        power = 0

    if power > maxword:
        power = maxword
    #print 'power',power
    sendFrame.append(power)

    # FREQUENCY OFFSET -------------------------------------
    if frequencyOffset == 0:
        frequencyOffset = int(5100)
    else:
        frequencyOffset

    if frequencyOffset < 0:
        frequencyOffset = 0

    if frequencyOffset > maxbyte:
        frequencyOffset = maxbyte
    #print 'frequencyOffset',frequencyOffset
    # cut in two the data
    sendFrame.append(frequencyOffset >> 8) # MSB
    sendFrame.append(frequencyOffset & 0xFF) # LSB


    # NUMBER OF PACKETS -------------------------------------
    if numberOfPackets == 0:
        numberOfPackets = int(1)
    else:
        numberOfPackets

    if numberOfPackets < 0:
        numberOfPackets = 0

    if numberOfPackets > maxbyte:
        numberOfPackets = maxbyte
    #print 'numberOfPackets',numberOfPackets
    # cut in two the data
    sendFrame.append(numberOfPackets >> 8) # MSB
    sendFrame.append(numberOfPackets & 0xFF) # LSB

    # LENGHT OF PACKETS -------------------------------------
    if lenghtOfPackets == 0:
        lenghtOfPackets = int(10) #default value
    else:
        lenghtOfPackets

    # manage argument limits (0-255) (see datasheet_LoRaBench_160617_A05_FirmwareSpecification_EN __ p6 __ Command sendFrames)
    if lenghtOfPackets < 0:
        lenghtOfPackets = 0

    if lenghtOfPackets > maxword:
        lenghtOfPackets = maxword
    #print 'lenghtOfPackets',lenghtOfPackets
    sendFrame.append(lenghtOfPackets)

    # DELAY --------------------------------------------------
    if delay == 0:
        delay = int(32) #default value
    else:
        delay

    # manage argument limits (0-255) (see datasheet_LoRaBench_160617_A05_FirmwareSpecification_EN __ p6 __ Command sendFrames)
    if delay < 0:
        delay = 0

    if delay > maxword:
        delay = maxword
    #print 'delay',delay
    sendFrame.append(delay)

    return sendFrame

def ComputeCrC (input_byte_array):

    # http://crcmod.sourceforge.net/crcmod.html#crcmod.Crc
    # for the polynomial, the value is for the LoRaBench documentation
    # and equaly, why use 0x18408 and not 0x8408 (see http://stackoverflow.com/questions/24851027/how-to-calculate-ansi-crc16-polynomial-0x8005-in-python3)
    crc16 = crcmod.mkCrcFun(0x11021,rev=True,initCrc=0, xorOut=0x0000)

    # creating the string format expected by crc16 (http://stackoverflow.com/questions/19210414/byte-array-to-hex-string)
    inputstr = binascii.hexlify(bytearray(input_byte_array))

    # Computing CRC16 (http://stackoverflow.com/questions/35205702/calculating-crc16-in-python)
    crc = crc16(inputstr.decode("hex"))
    return crc

def SendFrame (frameToSend):
    global ser
    #copy the input in list temporary for not touch to the input byte array because is re call a lot of times
    frameToSend_copy = list(frameToSend)

    #insert len in first position
    frameToSend_copy.insert(0, len(frameToSend_copy)+3 ) # for +3, see datasheet of LoRaBench send frame
    #print ("len and array:" + str(input_byte_array))

    crc = ComputeCrC (frameToSend_copy)

    frameToSend_copy.append(crc & 0xFF)
    frameToSend_copy.append(crc >> 8)
    #print input_byte_array

    #STX
    frameToSend_copy.insert(0, STX )
    #ETX
    frameToSend_copy.append(ETX)

    np.set_printoptions(formatter={'int':lambda x:hex(int(x))})
    #print( "Protocol command: " + str(np.array(input_byte_array_copy)))

    #send a frame to LoRaBench
    ser.write(frameToSend_copy) # wait to be sure the send message is done?

def LoRaBenchReceiveExpectedChar( expected_byte ):

    # initial byte read
    searchSTX = ser.read(1)

    # check loop
    while( len(searchSTX) != 0 ):

        # a byte has been received --> check its value
        received_byte = ord(searchSTX[0]) # byte to int conversion

        # if the irght one --> True
        if (expected_byte == received_byte):
            #print "STX reception success"
            return True
        # if the wrong one --> Try again
        else:
            print ("===> STX reception attempt failed: " + str(received_byte))
            searchSTX = ser.read(1)

    # timeout --> False
    #print "STX reception timeout"
    return False

def LoRaBenchReceiveChars( num_bytes ):

    return ser.read(num_bytes)

def ReceiveFrame():
    global ser

    if (ser.inWaiting() < 5):
        return []

    rxbufferlen = 0
    rxbuffer = []

    # receive STX
    if ( LoRaBenchReceiveExpectedChar( STX ) == False ):
        #print "No STX"
        return []

    # receive Length
    rxbuffer = LoRaBenchReceiveChars( 1 )
    if len(rxbuffer) == 0:
        print ""
        print ( "Empty frame reception" )
        return []
    else:
        rxbufferlen = ord(rxbuffer[0]) # byte to int conversion
        #print ""
        #print ( "Answer Lenght is: " + str(rxbufferlen) )

    # rxbuffer is theorically the length of actual data + 3 (length itself + 2 bytes CRC)
    # however we already have received length, soi we should ask for one byte less
    # but ETX is not comprised within this length, and we still must receive it
    # the conclusion is that we can keep rxbufferlen as this for receiving the whole frame, ETX included
    np.set_printoptions(formatter={'int':lambda x:hex(int(x))})
    # receive frame
    rxbuffer = LoRaBenchReceiveChars( rxbufferlen )

    # convert to ascii to int    ( see : http://www.linuxnix.com/pfotd-python-ord-function-examples/)
    rxbuffer=[ord(i) for i in rxbuffer]
    #print ""
    #print( "Received frame: " + str(rxbuffer))
    #print( "Received frame: " + str(np.array(rxbuffer)))

    #for calculate the CRC, we need to add the length of frame
    rxbuffer.insert(0, rxbufferlen )
    # we add the lenght of rxbuffer again because the size has change
    rxbufferlen += 1
    #print( "Rx buffer len : " + str(rxbufferlen))

    # verify CRC16
    #to calculate the CRC the ETX byte and the CRC bytes aren't used
    rxbufferCRC = rxbuffer[0:-3]
    #print rxbufferCRC

    #function to calculate the CRC16
    crcCalculate = ComputeCrC (rxbufferCRC)
    #print ("the CRC value is : " + str(crcCalculate))
    #print ("the rxbuffer is : " + str(rxbuffer))

    temp = rxbuffer[rxbufferlen-3] * 256 + ( rxbuffer[rxbufferlen-2])
    #print ("rxbuffer[rxbufferlen-3] : " + str(rxbuffer[rxbufferlen-3]))
    #print ("rxbuffer[rxbufferlen-2] : " + str(rxbuffer[rxbufferlen-2]))
    #print ("temp : " + str(temp))
    hexcrc = hex (crcCalculate)
    if crcCalculate != temp:
        print (" Wrong CRC")
        return []
    #else:
        #print ""
        #print ("Valid CRC : " + str(hexcrc))
        #print ""


    # verify that last byte is ETX
    if (rxbuffer[rxbufferlen-1] != ETX):
        print ("===> ETX reception failed: " + str(rxbuffer[rxbufferlen-1]))
        return []
    #else :
        #print ""
        #print "ETX reception success"

    #Check if the message inside buffer is the start TX answer or the stop TX answer


    print "rxbuffer",rxbuffer
    return rxbuffer[1:-3]
    #return rxbuffer[]

def TxRFframe(timeout = 2):

    frameToSend = CreateFrame()
    SendFrame(frameToSend)
    for i in xrange(timeout * 10):
        receiveFrame = ReceiveFrame()
        if 0 < len(receiveFrame):
            if (receiveFrame[0] == 0x84 ) and (receiveFrame[1] == 0x00 ):
                return True
            else:
                raise Exception("bad receive frame" , receiveFrame)
        time.sleep(0.1)

    return False

def EndRfFrame():
    receiveFrame = ReceiveFrame()
    if 0 < len(receiveFrame):
        if (receiveFrame[0] == 0x80 ) and (receiveFrame[1] == 0x04 ):
            return True
        else:
            return False
