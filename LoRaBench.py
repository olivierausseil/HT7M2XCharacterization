#!/usr/bin/python2

import serial
import crcmod
import binascii
import numpy as np

STX = 0x02
ETX = 0x03

def LoRaBenchInit():
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
Å	print("Using USB0")
    except:
        ser = serial.Serial(
            port='/dev/ttyUSB0',
            baudrate = 9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
            )
	print("Using USB1")


def ComputeCrC (input_byte_array):

    # http://crcmod.sourceforge.net/crcmod.html#crcmod.Crc
    # for the polynomial, the value is for the LoRaBench documentation
    # and equaly, why use 0x18408 and not 0x8408 (see http://stackoverflow.com/questions/24851027/how-to-calculate-ansi-crc16-polynomial-0x8005-in-python3)
    crc16 = crcmod.mkCrcFun(0x11021,rev=True,initCrc=0, xorOut=0x0000)

    #print ("initial array:" + str(input_byte_array))

    # creating the string format expected by crc16 (http://stackoverflow.com/questions/19210414/byte-array-to-hex-string)
    inputstr = binascii.hexlify(bytearray(input_byte_array))
    #print inputstr

    # Computing CRC16 (http://stackoverflow.com/questions/35205702/calculating-crc16-in-python)
    crc = crc16(inputstr.decode("hex"))
    #print crc
    #print hex(crc)
    return crc

def LoRaBenchSendFrame(input_byte_array):

    global ser

    #insert len in first position
    input_byte_array.insert(0, len(input_byte_array)+3 )
    #print ("len and array:" + str(input_byte_array))


    crc = ComputeCrC (input_byte_array)


    input_byte_array.append(crc & 0xFF)
    input_byte_array.append(crc >> 8)
    #print input_byte_array

    #STX
    input_byte_array.insert(0, STX )
    #ETX
    input_byte_array.append(ETX)

    np.set_printoptions(formatter={'int':lambda x:hex(int(x))})
    print( "Protocol command: " + str(np.array(input_byte_array)))

    #send a frame to LoRaBench
    ser.write(input_byte_array)



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


def LoRaBenchReceiveFrame( ):

    global ser

    rxbufferlen = 0
    rxbuffer = []

    # receive STX
    if ( LoRaBenchReceiveExpectedChar( STX ) == False ):
        print "No STX"
        return []

    # receive Length
    rxbuffer = LoRaBenchReceiveChars( 1 )
    if len(rxbuffer) == 0:
        print ""
        print ( "Empty frame reception" )
        return []
    else:
        rxbufferlen = ord(rxbuffer[0]) # byte to int conversion
        print ""
        print ( "Answer Lenght is: " + str(rxbufferlen) )

    # rxbuffer is theorically the length of actual data + 3 (length itself + 2 bytes CRC)
    # however we already have received length, soi we should ask for one byte less
    # but ETX is not comprised within this length, and we still must receive it
    # the conclusion is that we can keep rxbufferlen as this for receiving the whole frame, ETX included
    np.set_printoptions(formatter={'int':lambda x:hex(int(x))})
    # receive frame
    rxbuffer = LoRaBenchReceiveChars( rxbufferlen )

    # convert to ascii to int    ( see : http://www.linuxnix.com/pfotd-python-ord-function-examples/)
    rxbuffer=[ord(i) for i in rxbuffer]
    print ""
    print( "Received frame: " + str(rxbuffer))
    print( "Received frame: " + str(np.array(rxbuffer)))

    #for calculate the CRC, we need to add the length of frame
    rxbuffer.insert(0, rxbufferlen )
    # we calculate the lenght of rxbuffer again because the size has change
    rxbufferlen = rxbufferlen + 1

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
    else:
        print ""
        print ("Valid CRC : " + str(hexcrc))


    # verify that last byte is ETX
    if (rxbuffer[rxbufferlen-1] != ETX):
        print ("===> ETX reception failed: " + str(rxbuffer[rxbufferlen-1]))
        return []
    #else :
        #print ""
        #print "ETX reception success"

    return rxbuffer[1:-3]
    #return rxbuffer[]
