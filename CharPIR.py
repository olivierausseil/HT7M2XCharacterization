#!/usr/bin/python2

import time as time
from log import logger
import PIRlibrary as PIR
import RF_transmitter as RF

import json

shiftStart = 0.001
shiftStop = -0.010
#nbOfSetting = 1
#sensitivityGain = 16
#sensitivityTrigger = 0
#triggerTime = 10

json_file = 'testConfigFile.json'
json_data = open(json_file)
data = json.load(json_data)
json_data.close()

RF.RfInit()
#we select the different configuration on json file
for j in data['parameter']:
    PIR.SetPIRparameters(j['sensitivityGain'],  j['sensitivityTrigger'], j['triggerTime'])

    timeout_TxFrame = j['timeout_TxFrame']
    timeoutPIRdetection = j['timeoutPIRdetection']
    #frameToSend = [0x04]
    for k in xrange(j['nbOfLoop']):

        try:
            if not RF.TxRFframe (timeout_TxFrame):
                logger.debug("configuration %d, Loop %d, timeout_TxFrame(value: %d)",j['configuration'], k+1, timeout_TxFrame)
            else:
                tsTxRf = time.time() + shiftStart # for log the delta time
                waitReceiveFrame = True
                if not PIR.PIRdetection (timeoutPIRdetection):
                    logger.debug("configuration %d, Loop %d, timeoutPIR (value: %d)",j['configuration'],k+1, timeoutPIRdetection )
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
                    deltaEndDetectRf = tsEndRfFrame - tsEndDetect

                    logger.info('configuration %d, Loop %d, delta start: %f, delta stop: %f',j['configuration'],k+1, deltaDetectRf, deltaEndDetectRf)
            time.sleep(2)
            print '------------------------------'
        except Exception as reason:
            logger.error(reason)
            time.sleep(2)
            print '------------------------------'
