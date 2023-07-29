# image_display.py
# 5/31/2023
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# This Python script uses the Watchdog library to monitor the selected directory
# for newly created FITS files

import logging
import os
import sys
import time
import asyncio

import pyds9
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

#### DS9 Image Display Parameters ####################
CMAP = '3 0.1' # first number is the contrast, second is bias
SHOW_RAW = True # display raw images
SHOW_PRC = False # display processed images
######################################################

class DS9_DISPLAY:
    def __init__(self, logName, path):
        self.logName = logName
        self.logger = logging.getLogger(self.logName)
        self.path = path
        
    async def start(self):    
        try:
            self.d = pyds9.DS9()
        except:
            print(repr(sys.exc_info()[0])+' '+repr(sys.exc_info()[1])+' '+repr(sys.exc_info()[2]))
        
        if not os.path.isdir(self.path):
            os.makedirs(self.path)

        #self.d.set("cmap "+CMAP)
        self.logger.debug(self.path)
        if SHOW_RAW and SHOW_PRC:
            patterns = [self.path+"*.fits"]
            ignore_patterns = []
        elif SHOW_RAW and not SHOW_PRC:
            patterns = [self.path+"raw-*"]
            ignore_patterns = [self.path+"prc-*"]
        elif not SHOW_RAW and SHOW_PRC:
            patterns = [self.path+"prc-*"]
            ignore_patterns = [self.path+"raw-*"]
        else:
            patterns = []
            ignore_patterns = []

        ignore_directories = True
        case_sensitive = False

        my_event_handler = PatternMatchingEventHandler(patterns, 
                                                       ignore_patterns, 
                                                       ignore_directories, 
                                                       case_sensitive)
        my_event_handler.on_created = self.on_created
        my_event_handler.on_any_event = self.on_any_event
        go_recursively = True

        my_observer = Observer()
        my_observer.schedule(my_event_handler, self.path, recursive=go_recursively)

        my_observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            my_observer.stop()
            my_observer.join()

    def on_any_event(self, event):
        self.logger.debug(f"EVENT: {event.src_path}")

    def on_created(self, event):
        """
        Sends the new FITS file path to the DS9 open

        Input:
        - event     The triggered event, containing the filename
        """

        self.logger.info(f"Created: {event.src_path}")
        self.d.set("frame clear")
        time.sleep(1)
        self.d.set("file "+event.src_path)
        time.sleep(1)
        self.d.set("zoom to fit")

async def image_display_test(loop, logName, path):
    ds9_display = DS9_DISPLAY(logName, path)
    await asyncio.gather(ds9_display.start())

if __name__ == "__main__":
    scriptName = os.path.basename(__file__)
    
    if len(sys.argv) != 2:
        sys.exit(f'\nERROR; 1 argumenta required; \nusage: python {scriptName} [image directory]')
    
    path = sys.argv[1]
    logName = 'ds9'

    LOG_FORMAT = '%(asctime)s.%(msecs)03dZ %(name)-10s %(levelno)s \
        %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(datefmt = "%Y-%m-%d %H:%M:%S", format = LOG_FORMAT)
    logger = logging.getLogger(logName)
    logger.setLevel(logging.DEBUG)
    logger.debug('~~~~~~starting log~~~~~~')

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(image_display_test(loop, logName, path))
    except KeyboardInterrupt:
        print('Exiting Program...')