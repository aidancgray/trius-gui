import logging
import asyncio
import sys
import os
import tkinter as tk

from asyncio import IncompleteReadError

SEND_MSG_HDR = '########## SENT ##########'
RCVD_MSG_HDR = '########## RCVD ##########'

class asyncTCP_client:
    def __init__(self, logName, host, port, qIn, qOut, status=None, guiCfg=None):
        self.logName = logName
        self.logger = logging.getLogger(self.logName)
        self.host = host
        self.port = port
        self.qIn = qIn
        self.qOut = qOut
        self.status = status
        self.guiCfg = guiCfg
    
    async def timeout(self, waitTime):
        await asyncio.sleep(waitTime)

    async def tcp_echo_client(self): 
        try:
            reader, writer = await asyncio.open_connection(self.host, self.port)

            if type(self.status) == tk.Label:
                self.status["text"] = "CONNECTED"
                self.status["bg"] = "lawn green"
            else:
                self.status = True
            
            flag = True
            if self.guiCfg == None:
                self.logger.info("Send commands below. Type Q to quit:")
                while flag:
                    try:        
                        message = input('$ ')
                        
                        if message.upper() == 'Q':
                            flag = False
                        
                        else:
                            writer.write(message.encode())
                            await writer.drain()
                            msgIn = await reader.readuntil(separator=b'DONE\n')
                            self.logger.info("Sent:     {}".format(message))
                            self.logger.info("Received: {}".format(msgIn))
                        
                    except IncompleteReadError as e1:
                        self.logger.error(f'Warning: peer disconnected')
                        flag = False
                        await writer.drain()
            else:
                while flag:
                    try:
                        if not self.qOut.empty():
                            msgOut = await self.qOut.get()
                            if msgOut != None:
                                #self.logger.debug(f'SENT: {msgOut}')
                                if type(self.guiCfg) == tk.Text:
                                        self.guiCfg.insert(tk.END, f'{SEND_MSG_HDR}\n')
                                        self.guiCfg.insert(tk.END, msgOut)
                                        self.guiCfg.insert(tk.END, '\n')
                                        self.guiCfg.see(tk.END)
                                writer.write(msgOut.encode())
                                await writer.drain()
                                msgIn = await reader.readuntil(separator=b'DONE\n')

                                if msgIn != None:
                                    #self.logger.debug(f'RCVD: {msgIn}')
                                    if type(self.guiCfg) == tk.Text:
                                        self.guiCfg.insert(tk.END, f'{RCVD_MSG_HDR}\n')
                                        self.guiCfg.insert(tk.END, msgIn)
                                        self.guiCfg.insert(tk.END, '\n')
                                        self.guiCfg.see(tk.END)
                                    await self.enqueue_qIn(msgIn)
                        
                        await asyncio.sleep(0.000001)
                    
                    except IncompleteReadError as e1:
                        self.logger.error(f'Warning: peer disconnected')
                        flag = False
                        await writer.drain()
            
            if type(self.status) == tk.Label:
                self.status["text"] = "DISCONNECTED"
                self.status["bg"] = "tomato"
            else:
                self.status = False

            writer.close()
            await writer.wait_closed()
        
        except asyncio.TimeoutError:
            self.logger.info("Camera Connection Timeout")
    
    async def enqueue_qIn(self, msg):
        if self.qIn.full():
            self.logger.warn(f'Message-In Queue is FULL')
        else:
            await self.qIn.put(msg)

async def run_asyncTCP_client_test(logName, host, port):
    qIn = asyncio.Queue()
    qOut = asyncio.Queue()
    tcp_client = asyncTCP_client(logName, host, port, qIn, qOut)
    await asyncio.gather(tcp_client.tcp_echo_client())

if __name__ == "__main__":
    scriptName = os.path.basename(__file__)
    if len(sys.argv) != 3:
        sys.exit(f'\nERROR; 2 arguments required; \nusage: python {scriptName} [HOST] [PORT]')
    
    host = sys.argv[1]
    port = sys.argv[2]
    
    logName = 'trius'
    
    LOG_FORMAT = '%(asctime)s.%(msecs)03dZ %(name)-10s %(levelno)s \
        %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(datefmt = "%Y-%m-%d %H:%M:%S", format = LOG_FORMAT)
    logger = logging.getLogger(logName)
    logger.setLevel(logging.DEBUG)
    logger.debug('~~~~~~starting log~~~~~~')

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_asyncTCP_client_test(logName, host, port))
    except KeyboardInterrupt:
        print('Exiting Program...')