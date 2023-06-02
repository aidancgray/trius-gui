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

import pyds9
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

#### DS9 Image Display Parameters ####################
CMAP = '3 0.1' # first number is the contrast, second is bias
SHOW_RAW = True # display raw images
SHOW_PRC = False # display processed images
######################################################

class DS9_DISPLAY:
    def __init__(self, path):
        self.path = path
        self.log_start()
        try:
            self.d = pyds9.DS9()
        except:
            print(repr(sys.exc_info()[0])+' '+repr(sys.exc_info()[1])+' '+repr(sys.exc_info()[2]))

        self.d.set("cmap "+CMAP)

        if SHOW_RAW and SHOW_PRC:
            patterns = [path+"*.fits"]
            ignore_patterns = []
        elif SHOW_RAW and not SHOW_PRC:
            patterns = [path+"raw-*"]
            ignore_patterns = [path+"prc-*"]
        elif not SHOW_RAW and SHOW_PRC:
            patterns = [path+"prc-*"]
            ignore_patterns = [path+"raw-*"]
        else:
            patterns = []
            ignore_patterns = []

        ignore_directories = True
        case_sensitive = True

        my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
        my_event_handler.on_created = self.on_created
        go_recursively = True

        my_observer = Observer()
        my_observer.schedule(my_event_handler, path, recursive=go_recursively)

        my_observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            my_observer.stop()
            my_observer.join()

    def log_start(self):
        """
        Create a logfile that the rest of the script can write to.

        Output:
        - log 	Object used to access write abilities
        """

        scriptDir = os.path.dirname(os.path.abspath(__file__))
        scriptName = os.path.splitext(os.path.basename(__file__))[0]
        self.log = logging.getLogger('file-watch')
        hdlr = logging.FileHandler(scriptDir+'/logs/'+scriptName+'.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.log.addHandler(hdlr)
        self.log.setLevel(logging.INFO)

    def on_created(self, event):
        """
        Sends the new FITS file path to the DS9 open

        Input:
        - event     The triggered event, containing the filename
        """
        global d
        self.log.info(f"Created: {event.src_path}")
        d.set("frame clear")
        d.set("file "+event.src_path)
        time.sleep(1)
        d.set("zoom to fit")
        
if __name__ == "__main__":
    path = sys.argv[1]
    log = log_start()
    try:
        d = pyds9.DS9()
    except:
        print(repr(sys.exc_info()[0])+' '+repr(sys.exc_info()[1])+' '+repr(sys.exc_info()[2]))
        #d = pyds9.DS9()

    d.set("cmap "+CMAP)

    if SHOW_RAW and SHOW_PRC:
        patterns = [path+"*.fits"]
        ignore_patterns = []
    elif SHOW_RAW and not SHOW_PRC:
        patterns = [path+"raw-*"]
        ignore_patterns = [path+"prc-*"]
    elif not SHOW_RAW and SHOW_PRC:
        patterns = [path+"prc-*"]
        ignore_patterns = [path+"raw-*"]
    else:
        patterns = []
        ignore_patterns = []

    ignore_directories = True
    case_sensitive = True

    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
    my_event_handler.on_created = on_created
    go_recursively = True

    my_observer = Observer()
    my_observer.schedule(my_event_handler, path, recursive=go_recursively)

    my_observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        my_observer.stop()
        my_observer.join()