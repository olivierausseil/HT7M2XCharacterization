#!/usr/bin/python2

import time as time
from log import logger
import PIRlibrary as PIR
import RF_transmitter as RF

shiftStart = 0.001
shiftStop = -0.010
nbOfSetting = 1
sensitivityGain = 16
sensitivityTrigger = 0
triggerTime = 10

for i in xrange(nbOfSetting):  # utiliser une boucle for

    PIR.SetPIRparameters(sensitivityGain,  sensitivityTrigger, triggerTime)
    RF.RfInit()
    #RF_sender_config()  # useless

    nbOfLoop = 20000
    timeout_TxFrame = 2
    timeoutPIRdetection = 5
    frameToSend = [0x04]
    for i in xrange(nbOfLoop):
        print 'Cycle', i
        try:
            if not RF.TxRFframe (frameToSend, timeout_TxFrame):
                #LogDebug('numero parametre', 'cptloop',timeoutnotsent)
                logger.debug("nb of loop: %d , timeout_TxFrame : %d", i, timeout_TxFrame)
            else:
                tsTxRf = time.time() + shiftStart # for log the delta time
                waitReceiveFrame = True
                if not PIR.PIRdetection (timeoutPIRdetection):
                    #LogDebug('numero parametre','cptloop', timeout_PIRdetection)
                    logger.debug("nb of loop: %d , timeoutPIR : %d",i, timeoutPIRdetection )
                    while waitReceiveFrame:
                        if RF.EndRfFrame():
                            'print EndRfFrame ok'
                            waitReceiveFrame = False
                else:
                    tsDetect = time.time()
                    waitDetection = True
                    waitReceiveFrame = True
                    while waitDetection or waitReceiveFrame:
                        if waitDetection:
                            if PIR.PIRendDetection():
                                tsEndDetect = time.time()
                                waitDetection = False
                        if waitReceiveFrame:
                            if RF.EndRfFrame():
                                tsEndRfFrame = time.time() + shiftStop
                                waitReceiveFrame = False

                        time.sleep(0.001)

                    deltaDetectRf = tsDetect - tsTxRf
                    deltaEndDetectRf = tsEndDetect - tsEndRfFrame

                    #logEvent('numero parametre' , 'cptloop', deltaDetectRf, deltaDetectRf)
                    logger.info('nb of loop : %d , delta start : %f, delta stop : %f',i, deltaDetectRf, deltaEndDetectRf)
                    time.sleep(2)
        except Exception as reason:
            logger.error(reason)
