import logging
import asyncio
import sys
import os
import subprocess
import tkinter as tk

class msgHdlr:
    def __init__(self, logName, qIn, qOut, console, localDir):
        self.logName = logName
        self.qIn = qIn
        self.qOut = qOut
        self.console = console
        path = localDir
        if not os.path.isdir(path):
            os.makedirs(path)
        self.localDir = path

    async def start(self):
        while True:
            if not self.qIn.empty():
                rawMsg = await self.qIn.get()
                rawMsg = rawMsg.decode("utf-8")

                retMsg = await self.parse_raw_message(rawMsg)
                await self.enqueue_qOut(retMsg)
            await asyncio.sleep(0.000001)

    async def parse_raw_message(self, msg):
        # msgList = msg.split("=")
        # if type(self.console) == tk.Text:
        #     self.console.insert(tk.END, msgList)
        #     self.console.see(tk.END)
        if "COMMAND = EXPOSE" in msg:
            if "FILENAME = " in msg:
                remoteDirIdxStart = msg.find("FILENAME = ")+11
                remoteDirIdxStop = msg.find('\n', remoteDirIdxStart)
                remoteDir = msg[remoteDirIdxStart:remoteDirIdxStop]
                fileName = remoteDir[remoteDir.find("raw-"):]
                os.system(f"rsync -avzh --progress --recursive idg@172.16.1.127:{remoteDir} {self.localDir}{fileName}")
                os.system(f"touch {self.localDir}{fileName}")
                

    async def enqueue_qOut(self, msg):
        if self.qOut.full():
            self.logger.warn(f'Message-Out Queue is FULL')
        else:
            await self.qOut.put(msg)
    
    async def enqueue_qIn(self, msg):
        if self.qIn.full():
            self.logger.warn(f'Message-Out Queue is FULL')
        else:
            await self.qIn.put(msg)