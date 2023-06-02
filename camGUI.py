import asyncio
import logging
import os
import sys
import time
import tkinter as tk
from tkinter import font
from image_display import DS9_DISPLAY

import pyds9


class camGUI_App:
    def __init__(self, inQ, outQ):
        self.inQ = inQ
        self.outQ = outQ

    async def exec(self):
        self.window = camGUI_Window(asyncio.get_event_loop(), 
                                    self.inQ, self.outQ)
        await self.window.show()

class camGUI_Window(tk.Tk):
    def __init__(self, loop, inQ, outQ):
        self.logger = logging.getLogger('camGUI')
        self.loop = loop
        self.inQ = inQ
        self.outQ = outQ
        self.connStatus = False
        
        self.root = tk.Tk()
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family='Helvetica',
                               size=18
                               )
        self.root.title("SX Trius Camera Control")

        ########## Connection Frame ##########
        self.frm_conn = tk.Frame(master=self.root)
        self.frm_conn.grid(row=0, column=0, padx=50, pady=0)

        self.lbl_hostIP = tk.Label(master=self.frm_conn, text="Host IP:")
        self.lbl_hostIP.grid(row=0, column=0, sticky='E')
        self.lbl_hostPort = tk.Label(master=self.frm_conn, text="Host Port:")
        self.lbl_hostPort.grid(row=1, column=0, sticky='E')

        self.ent_hostIP = tk.Entry(master=self.frm_conn)
        self.ent_hostIP.grid(row=0, column=1, sticky='W')
        self.ent_hostIP.insert(0, "172.16.1.127")

        self.ent_hostPort = tk.Entry(master=self.frm_conn)
        self.ent_hostPort.grid(row=1, column=1, sticky='W')
        self.ent_hostPort.insert(0, "9999")

        self.btn_connect = tk.Button(
            master=self.frm_conn,
            text="-",
            command=lambda: self.loop.create_task(self.flipConn())
            )
        self.btn_connect.grid(row=2, column=0, columnspan=2, pady=10)

        if self.connStatus:
            self.lbl_status = tk.Label(master=self.frm_conn, text="CONNECTED")
            self.btn_connect["text"] = "DISCONNECT"
            self.lbl_status["bg"] = "green"
        else:
            self.lbl_status = tk.Label(master=self.frm_conn, text="DISCONNECTED")
            self.btn_connect["text"] = "CONNECT"
            self.lbl_status["bg"] = "red"
        self.lbl_status.grid(row=3, column=0, columnspan=2, pady=20)

        ########## DS9 GUI Frame ##########
        self.frm_ds9 = tk.Frame(master=self.root)
        self.frm_ds9.grid(row=1, column=0, padx=50, pady=0)

        self.lbl_imgDir = tk.Label(master=self.frm_ds9, text="Image Directory:")
        self.lbl_imgDir.grid(row=0, column=0, sticky='E')

        path_var=tk.StringVar()
        self.ent_imgDir = tk.Entry(master=self.frm_ds9, textvariable=path_var)
        self.ent_imgDir.grid(row=0, column=1, sticky='W')
        self.ent_imgDir.insert(0, "~/Pictures/Trius_Cam")

        self.btn_ds9 = tk.Button(
            master=self.frm_ds9,
            text="Open DS9",
            command=lambda: self.loop.create_task(self.openDS9(path_var.get()))
            )
        self.btn_ds9.grid(row=1, column=0, columnspan=2, pady=10)

        ########## Bottom Frame ##########
        self.frm_bottom = tk.Frame(master=self.root)
        self.frm_bottom.grid(row=2, column=0, padx=50, pady=10)
        self.btn_close = tk.Button(
            master=self.frm_bottom,
            text="CLOSE",
            command=lambda: self.loop.create_task(self.exitApp())
            )
        self.btn_close.grid(row=0, column=0)
        
    async def show(self):
        while True:
            self.root.update()
            await asyncio.sleep(0.01)

    async def flipConn(self):
        if self.connStatus:
            self.connStatus = False
            self.lbl_status["text"] = "DISCONNECTED"
            self.btn_connect["text"] = "CONNECT"
            self.lbl_status["bg"] = "red"
        else:
            self.connStatus = True
            self.lbl_status["text"] = "CONNECTED"
            self.btn_connect["text"] = "DISCONNECT"
            self.lbl_status["bg"] = "green"
    
    async def openDS9(self, path):
        self.ds9 = DS9_DISPLAY(path)

    async def exitApp(self):
        raise KeyboardInterrupt

async def camGUI_Test():
    await asyncio.gather(camGUI_App().exec())

if __name__ == "__main__":
    LOG_FORMAT = '%(asctime)s.%(msecs)03dZ %(name)-10s %(levelno)s \
        %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(datefmt = "%Y-%m-%d %H:%M:%S", format = LOG_FORMAT)
    logger = logging.getLogger('camGUI')
    logger.setLevel(logging.DEBUG)
    logger.debug('~~~~~~starting log~~~~~~')

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(camGUI_Test())
    except KeyboardInterrupt:
        print('Exiting Program...')
    