# The skeleton for characterize the PIR sensor
shiftStart = 1
shiftStop = -10
while True:  # utiliser une boucle for
    if (userNewParameter == ): # maybe useless
        PIR_config()
        RF_sender_config()

    nbOfLoop = Ask Nb_of_loop ? # utiliser un for

    while (nbOfLoop == CptOfLoop): # Utiliser une boucle for
        if not TxRFframe ():
            LogDebug('numero parametre', 'cptloop',notsent)
        else:
            tsTxRf = time.time() + shiftStart # for log the delta time
            waitReceiveFrame = True
            if not PIRdetection (timeout):
                LogDebug('numero parametre','cptloop', timeout)
                while waitReceiveFrame:
                    if waitReceiveFrame:
                        if endRfFrame():
                            waitReceiveFrame = False
            else:
                tsDetect = time.time()
                waitDetection = True
                waitReceiveFrame = True
                while waitDetection or waitReceiveFrame:
                    if waitDetection:
                        if PIRendDetection():
                            tsEndDetect = time.time()
                            waitDetection = False
                    if waitReceiveFrame:
                        if endRfFrame():
                            tsEndRfFrame = time.time() + shiftStop
                            waitReceiveFrame = False
                    time.sleep(0.001)

                deltaDetectRf = tsDetect - tsTxRf
                deltaEndDetectRf = tsEndDetect - tsEndRfFrame
                logEvent('numero parametre' , 'cptloop', deltaDetectRf, deltaDetectRf)

        time.sleep(2)
        CptOfLoop += 1










# To the begining of the program, we need to determine the different parameter
#   for the different module use for the Characterization.
# Also, after a number of cycle test with parameter, we can change,
#   if a user want, the parameter of the different module.


# Call a function to send radio wave frame on the RF transmitter.
# TxRFframe can be send a serial ask to, in our case, the LoRaBench and recover this answer know if the wave emission are OK (return of the function).
# After some test on the LoRaBench, we know that the emission wave begin beforethe end of the serial answer (1.5ms). Like this time is very short, we consider that two moment occur at the same moment.

# After the radio emission, we wait a detection by the sensor.
# The function return if the detection occur or not.
# A timeout is necessary if the sensor does not capture anything.
# A funtion return a log in any case to know the sensor behavior.


# if the flag is high, we don't need anymore to use the PIRendDetection function
    # This function return two parameter, the first simply to tell the end of detection,
    #   the other, a sflag for check after if the end detection occur before the LoRaBench answer

    # This function return two parameter, the first simply to tell that the frame is receive by the serial bus,
    #   the other, a flag for check after if the the LoRaBench answer occur before end detection
