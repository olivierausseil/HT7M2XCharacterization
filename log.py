#!/usr/bin/python2

import logging
import time

# sources
#http://deusyss.developpez.com/tutoriels/Python/Logger/
#http://sametmax.com/ecrire-des-logs-en-python/
# Desire format
formatter = logging.Formatter("%(asctime)s -- %(levelname)s -- %(message)s")
formatter2 = logging.Formatter("%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s")
formatter3 = logging.Formatter("%(asctime)s - %(message)s")
formatter4 = logging.Formatter("%(asctime)s - %(message)s","%H:%M:%S")

#creation of handler who permit to separate the different log level
#handler_critic = logging.FileHandler("critic.log", mode="a", encoding="utf-8")
handler_debug = logging.FileHandler("/home/pi/logFile/Characterization.csv", mode="a", encoding="utf-8")
#handler_warning = logging.FileHandler("warning.log", mode="a", encoding="utf-8")

#set the format of message to handler
#handler_critic.setFormatter(formatter)
handler_debug.setFormatter(formatter)
#handler_warning.setFormatter(formatter)

#set level to handler
handler_debug.setLevel(logging.DEBUG)
#handler_critic.setLevel(logging.CRITICAL)
#handler_warning.setLevel(logging.WARNING)

# We create an object with logger type, we assigns a minimum level (logging.INFO) and use with the handler created
logger = logging.getLogger()
logger.setLevel(logging.DEBUG) # ***
#logger.addHandler(handler_critic)
logger.addHandler(handler_debug)
#logger.addHandler(handler_warning)

#Permit to transmit log message
#logger.debug('Debug error') # minimum level is INFO(see ***), so the debug log don't appear (see level of logging)
#logger.info('INFO ERROR')
#logger.critical('INFO ERROR2')

# creation of handler to display on terminal
steam_handler = logging.StreamHandler()
steam_handler.setLevel(logging.DEBUG)
logger.addHandler(steam_handler)
