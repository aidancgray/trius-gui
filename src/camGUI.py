import subprocess
import asyncio
import logging
import os
import sys
import time
import tkinter as tk
from datetime import datetime 
from tkinter import font
from image_display import DS9_DISPLAY
from asyncTCP_client import asyncTCP_client
from msgHandler import msgHdlr

GEN_FRAME_W = 400
GEN_FRAME_H = 150
GEN_COL_MINSIZE = 200
GEN_PADX = 0
GEN_PADY = 10

GEN_RELIEF = tk.RAISED
GEN_BRDR_W = 4

BG_COLOR = 'light gray'
W_COLOR = 'light gray'
SUB_W_COLOR = 'white'

################################################################################
class camGUI_App():
    def __init__(self, logName, qIn, qOut):
        self.logName = logName
        self.qIn = qIn
        self.qOut = qOut
        self.p = None

    async def exec(self):
        self.window = camGUI_Window(asyncio.get_event_loop(), 
                                    self.logName,
                                    self.qIn, self.qOut)
        await self.window.show()

class camGUI_Window(tk.Tk):
    def __init__(self, loop, logName, qIn, qOut):
        self.now = datetime.now().strftime("%m-%d-%Y")
        self.default_directory = f"~/src/cam-pics/{self.now}/"
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
        #self.conn_root.grid_columnconfigure(0, weight=1)

        ########## DS9 GUI Frame ##########
        self.frm_ds9 = tk.Frame(master=self.conn_root, 
                                relief=GEN_RELIEF, borderwidth=GEN_BRDR_W,
                                width=GEN_FRAME_W, height=80
                                )
        self.frm_ds9.grid(row=0, column=0, padx=10, pady=10, ipadx=10, ipady=10)
        self.frm_ds9["bg"] = SUB_W_COLOR
        self.frm_ds9.grid_propagate(False)

        self.lbl_imgDir = tk.Label(master=self.frm_ds9, text="Image Directory:")
        self.lbl_imgDir.grid(row=0, column=0, sticky='nesw')

        self.ent_imgDir = tk.Entry(master=self.frm_ds9,
                                   font=('Courier', '16')
                                   )
        self.ent_imgDir.grid(row=0, column=1, sticky='ew')

        self.ent_imgDir.insert(0, self.default_directory)

        self.btn_ds9 = tk.Button(
            master=self.frm_ds9,
            text="Open DS9",
            command=lambda: self.display_images(self.ent_imgDir.get())
            )
        self.btn_ds9.grid(row=1, column=0, columnspan=2, sticky='nesw')

        self.frm_ds9.columnconfigure(0,weight=5, uniform='ds9C')
        self.frm_ds9.columnconfigure(1,weight=8, uniform='ds9C')
        self.frm_ds9.rowconfigure(0,weight=1, uniform='ds9R')
        self.frm_ds9.rowconfigure(1,weight=1, uniform='ds9R')

        ########## Connection Frame ##########
        self.frm_conn = tk.Frame(master=self.conn_root,
                                 width=GEN_FRAME_W, height=120, 
                                 relief=GEN_RELIEF, borderwidth=GEN_BRDR_W,
                                 )
        self.frm_conn.grid(row=1, column=0, padx=10, pady=10, ipadx=10, ipady=10)
        self.frm_conn["bg"] = SUB_W_COLOR
        self.frm_conn.grid_propagate(False)

        self.lbl_hostIP = tk.Label(master=self.frm_conn, text="Host IP:")
        self.lbl_hostIP.grid(row=0, column=0, sticky='e')
        self.lbl_hostPort = tk.Label(master=self.frm_conn, text="Host Port:")
        self.lbl_hostPort.grid(row=1, column=0, sticky='e')

        self.ent_hostIP = tk.Entry(master=self.frm_conn,
                                   font=('Courier', '16')
                                   )
        self.ent_hostIP.grid(row=0, column=1, sticky='ew')
        self.ent_hostIP.insert(0, "172.16.1.127")

        self.ent_hostPort = tk.Entry(master=self.frm_conn,
                                     font=('Courier', '16')
                                     )
        self.ent_hostPort.grid(row=1, column=1, sticky='ew')
        self.ent_hostPort.insert(0, "9999")

        self.btn_connect = tk.Button(
            master=self.frm_conn,
            text="",
            command=lambda: self.loop.create_task(self.connectToHost())
            )
        self.btn_connect.grid(row=2, column=0, sticky='nesw') 
        
        self.lbl_status = tk.Label(
            master=self.frm_conn, 
            text="DISCONNECTED", 
            relief=tk.SUNKEN, borderwidth=GEN_BRDR_W)
        self.btn_connect["text"] = "CONNECT"
        self.lbl_status["bg"] = "tomato"
        self.lbl_status.grid(row=2, column=1, sticky='nesw')

        self.frm_conn.columnconfigure(0,weight=1, uniform='connC')
        self.frm_conn.columnconfigure(1,weight=1, uniform='connC')
        
        self.frm_conn.rowconfigure(0,weight=1, uniform='connR')
        self.frm_conn.rowconfigure(1,weight=1, uniform='connR')
        self.frm_conn.rowconfigure(2,weight=1, uniform='connR')

        ########## Cam Control Frame ##########
        self.frm_ctl = tk.Frame(master=self.conn_root,
                                relief=GEN_RELIEF, borderwidth=GEN_BRDR_W,
                                width=GEN_FRAME_W, height=100
                                )
        self.frm_ctl.grid(row=2, column=0, padx=10, pady=10, ipadx=10, ipady=10)
        self.frm_ctl["bg"] = SUB_W_COLOR
        self.frm_ctl.grid_propagate(False)
        
        self.lbl_commands = tk.Label(master=self.frm_ctl, 
                                    text="Camera Commands"
                                    )
        self.lbl_commands.grid(row=0, column=0,columnspan=3, sticky='w')
        
        self.btn_status = tk.Button(
            master=self.frm_ctl,
            text="Status",
            relief=tk.RAISED, borderwidth=GEN_BRDR_W,
            state=tk.DISABLED,
            #width=10,
            command=lambda: self.loop.create_task(self.enqueue_qOut("status"))
        )
        self.btn_status.grid(row=1, column=0, columnspan=1, sticky='nesw')

        self.btn_expose = tk.Button(
            master=self.frm_ctl,
            text="Expose",
            relief=tk.RAISED, borderwidth=GEN_BRDR_W,
            state=tk.DISABLED,
            #width=10,
            command=lambda: self.loop.create_task(self.cam_expose())
        )
        self.btn_expose.grid(row=2, column=0, columnspan=1, sticky='nesw')

        vcmd_float = self.frm_ctl.register(self.validate_float)
        self.ent_expTime = tk.Entry(master=self.frm_ctl, 
                                    state=tk.DISABLED, 
                                    validate='key',
                                    justify='right',
                                    font=('Courier', '16'),
                                    validatecommand=(vcmd_float, '%P')
                                    )
        self.ent_expTime.grid(row=2, column=1, columnspan=1, sticky='nesw')

        lbl_s = tk.Label(master=self.frm_ctl, text='s')
        lbl_s.grid(row=2, column=2, sticky='nesw')

        self.frm_ctl.columnconfigure(0,weight=5, uniform='ctlC')
        self.frm_ctl.columnconfigure(1,weight=5, uniform='ctlC')
        self.frm_ctl.columnconfigure(2,weight=1, uniform='ctlC')
        self.frm_ctl.rowconfigure(0,weight=1, uniform='ctlR')
        self.frm_ctl.rowconfigure(1,weight=1, uniform='ctlR')
        self.frm_ctl.rowconfigure(2,weight=1, uniform='ctlR')

        ########## Console Frame ##########
        self.frm_console = tk.Frame(master=self.conn_root, 
                                    relief=GEN_RELIEF, borderwidth=GEN_BRDR_W,
                                    width=GEN_FRAME_W, #height=200
                                    )
        self.frm_console.grid(row=3, column=0, padx=10, pady=10, ipadx=10, ipady=10)
        self.frm_console["bg"] = SUB_W_COLOR
        #self.frm_console.grid_propagate(False)

        self.lbl_console = tk.Label(master=self.frm_console, 
                                    text="Console Output"
                                    )
        self.lbl_console.grid(row=0, column=0, sticky='W')

        self.consoleOut = tk.Text(master=self.frm_console,
                                  width=52, height=20,
                                  font=('Courier', '12')
                                  )
        self.consoleOut.grid(row=1, column=0, 
                             padx=10, pady=0, 
                             sticky='nesw')

        ########## Bottom Frame ##########
        # self.frm_bottom = tk.Frame(master=self.conn_root, 
        #                            relief=GEN_RELIEF, borderwidth=GEN_BRDR_W, 
        #                            width=GEN_FRAME_W
        #                            )
        # self.frm_bottom.grid(row=4, column=0, padx=GEN_PADX, pady=GEN_PADY)
        # self.frm_bottom["bg"] = SUB_W_COLOR

        self.btn_close = tk.Button(
            master=self.conn_root,
            width=10, height=2,
            text="CLOSE",
            command=lambda: self.loop.create_task(self.exitApp())
            )
        self.btn_close.grid(row=4, column=0, pady=20)
        self.btn_close.config(relief='raised')

        #self.conn_root.grid_rowconfigure(0, weight=1)
        #self.conn_root.grid_columnconfigure(index=0, minsize=400)
        #self.conn_root.grid_columnconfigure(index=1, minsize=400)

    async def connectToHost(self):
        if self.lbl_status["text"] == "CONNECTED":
            self.lbl_status["text"] = "DISCONNECTED"
            self.lbl_status["bg"] = "tomato"
            for task in self.connTasks:
                    task.cancel()

        elif self.lbl_status["text"] == "DISCONNECTED":
            imgDir = self.ent_imgDir.get()
            if imgDir[0] == '~':
                imgDir = os.path.expanduser('~')+imgDir[1:]
            if imgDir[len(imgDir)-1] != '/':
                imgDir = imgDir + '/'

            self.msgHdlr = msgHdlr(self.logName,
                                   self.qIn,
                                   self.qOut,
                                   self.consoleOut,
                                   imgDir)

            self.tcpClient = asyncTCP_client(self.logName, 
                                             self.ent_hostIP.get(), 
                                             self.ent_hostPort.get(), 
                                             self.qIn, 
                                             self.qOut,
                                             status=self.lbl_status, 
                                             guiCfg=self.consoleOut)
            
            self.connTasks = [
                # asyncio.create_task(self.timeout(3, connQueue)),
                asyncio.create_task(self.msgHdlr.start()),
                asyncio.create_task(self.tcpClient.tcp_echo_client())
            ]
            taskGroup = asyncio.gather(*self.connTasks)
            try:
                await taskGroup
            except asyncio.TimeoutError:
                logger.setLevel(logging.WARNING)
                logger.warning('Connection timed out')
                for task in self.connTasks:
                    task.cancel()
            except Exception as e:
                logger.setLevel(logging.WARNING)
                logger.warning(f'Exception: {e}\nCancelling Running Tasks...')
                for task in self.connTasks:
                    task.cancel()
    
    async def timout(self, time, connQueue):
        await asyncio.sleep(time)
        if connQueue.isEmpty():
            raise asyncio.TimeoutError

    async def openDS9(self):
        imgDir = self.ent_imgDir.get()
        if imgDir[len(imgDir)-1] != '/':
                imgDir = imgDir + '/'
                
        ds9_display = DS9_DISPLAY(self.logName, imgDir)
        await asyncio.gather(ds9_display.start())

    def display_images(self, fileDir):
        """
        Runs the image_display.py script on the given directory.
        This script watches for FITS files starting with 'raw-'
        and displays them in a DS9 window.

        Input:
        - fileDir   Directory on THIS MACHINE to watch.

        Output:
        - subprocess object
        """

        if fileDir[0] == '~':
            fileDir = os.path.expanduser('~')+fileDir[1:]

        # kill process if it's already running
        try:
            if self.p.poll() is None:
                self.p.kill()
            print("Image_Display script watching dir: "+fileDir)
            return subprocess.Popen(['python', 'image_display.py', fileDir], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except:
            print("Image_Display script watching dir: "+fileDir)
            return subprocess.Popen(['python', 'image_display.py', fileDir], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    def validate_float(self, text):
        if (all(char in "0123456789." for char in text) and  # all characters are valid
            text.count(".") <= 1): # only 0 or 1 periods
                return True
        else:
            return False
        
    async def cam_expose(self):
        time = self.ent_expTime.get()
        expCmd = f'expose light {time}'
        await self.enqueue_qOut(expCmd)

    async def enqueue_qOut(self, msg):
        if self.qOut.full():
            self.logger.warn(f'Message-In Queue is FULL')
        else:
            await self.qOut.put(msg)

    async def show(self):
        while self.winShow:
            if self.lbl_status["text"] == "DISCONNECTED":
                self.btn_connect["text"] = "CONNECT"
                self.btn_status["state"] = tk.DISABLED
                self.btn_expose["state"] = tk.DISABLED
                self.ent_expTime["state"] = tk.DISABLED
            elif self.lbl_status["text"] == "CONNECTED":
                self.btn_connect["text"] = "DISCONNECT"
                self.btn_status["state"] = tk.NORMAL
                self.btn_expose["state"] = tk.NORMAL
                self.ent_expTime["state"] = tk.NORMAL

            self.conn_root.update()
            await asyncio.sleep(0.01)

    async def exitApp(self):
        self.winShow = False
        self.conn_root.destroy()

async def camGUI_Test(logName):
    qIn = asyncio.Queue()
    qOut = asyncio.Queue()
    await asyncio.gather(camGUI_App(logName, qIn, qOut).exec())

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
    