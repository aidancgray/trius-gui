import subprocess
import asyncio
import logging
import os
import sys
import time
import tkinter as tk
from tkinter import font
from image_display import DS9_DISPLAY
from asyncTCP_client import asyncTCP_client
from msgHandler import msgHdlr

GEN_FRAME_W = 500

GEN_PADX = 0
GEN_PADY = 10

GEN_RELIEF = tk.RAISED
GEN_BRDR_W = 4

BG_COLOR = 'light gray'
W_COLOR = 'light gray'
SUB_W_COLOR = 'white'

################################################################################
class connGUI_App():
    def __init__(self, logName, qIn, qOut):
        self.logName = logName
        self.qIn = qIn
        self.qOut = qOut
        self.p = None

    async def exec(self):
        self.window = connGUI_Window(asyncio.get_event_loop(), 
                                    self.logName,
                                    self.qIn, self.qOut)
        await self.window.show()

class connGUI_Window(tk.Tk):
    def __init__(self, loop, logName, qIn, qOut):
        self.logName = logName
        self.logger = logging.getLogger(self.logName)
        self.loop = loop
        self.qIn = qIn
        self.qOut = qOut
        self.connStatus = False
        self.winShow = True

        self.conn_root = tk.Tk()
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family='Helvetica',
                               size=18)
        
        self.conn_root.title("SX Trius Camera - Connection")
        self.conn_root["bg"] = BG_COLOR

        ########## Connection Frame ##########
        self.frm_conn = tk.Frame(master=self.conn_root,
                                 width=500, height=500,
                                 relief=GEN_RELIEF, borderwidth=GEN_BRDR_W,
                                 )
        self.frm_conn.grid(row=0, column=0, padx=50, pady=GEN_PADY)
        self.frm_conn["bg"] = SUB_W_COLOR
        self.frm_conn.grid_propagate(False)

        self.lbl_hostIP = tk.Label(master=self.frm_conn, text="Host IP:")
        self.lbl_hostIP.grid(row=0, column=0, sticky=tk.W)
        # self.lbl_hostPort = tk.Label(master=self.frm_conn, text="Host Port:")
        # self.lbl_hostPort.grid(row=1, column=0, sticky=tk.W)

        # self.ent_hostIP = tk.Entry(master=self.frm_conn)
        # self.ent_hostIP.grid(row=0, column=1, sticky=tk.W)
        # self.ent_hostIP.insert(0, "172.16.1.127")

        # self.ent_hostPort = tk.Entry(master=self.frm_conn)
        # self.ent_hostPort.grid(row=1, column=1, sticky=tk.W)
        # self.ent_hostPort.insert(0, "9999")

    async def show(self):
        while self.winShow:
            self.conn_root.update()
            await asyncio.sleep(0.01)

    async def exitApp(self):
        self.winShow = False
        self.conn_root.destroy()
        #raise KeyboardInterrupt

async def camGUI_Test(logName):
    qIn = asyncio.Queue()
    qOut = asyncio.Queue()
    await asyncio.gather(connGUI_App(logName, qIn, qOut).exec())

if __name__ == "__main__":
    logName = 'camGUI'
    LOG_FORMAT = '%(asctime)s.%(msecs)03dZ %(name)-10s %(levelno)s \
        %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(datefmt = "%Y-%m-%d %H:%M:%S", format = LOG_FORMAT)
    logger = logging.getLogger(logName)
    logger.setLevel(logging.DEBUG)
    logger.debug('~~~~~~starting log~~~~~~')

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(camGUI_Test(logName))
    except KeyboardInterrupt:
        print('Exiting Program...')
    