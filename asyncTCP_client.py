import logging
import asyncio
import sys
import os

#from asyncio.exceptions import IncompleteReadError

class asyncTCP_client:
    def __init__(self, host, port, inQ, outQ):
        self.logger = logging.getLogger('trius')
        self.host = host
        self.port = port
        self.inQ = inQ
        self.outQ = outQ   

    async def tcp_echo_client(self):
        reader, writer = await asyncio.open_connection(self.host, self.port)
        
        self.logger.info("Send commands below. Type Q to quit:")
        
        flag = True
        while flag:
            
            message = input('$ ')
            
            if message.upper() == 'Q':
                flag = False
            
            else:
                writer.write(message.encode())
                data = await reader.readuntil(separator=b'DONE\n')

                self.logger.info("Sent:     {}".format(message))
                self.logger.info("Received: {}".format(data))

            writer.close()

async def run_asyncTCP_client_test(host, port):
    tcp_client = asyncTCP_client(host, port)
    await asyncio.gather(tcp_client.tcp_echo_client())

if __name__ == "__main__":
    scriptName = os.path.basename(__file__)
    if len(sys.argv) != 3:
        sys.exit(f'\nERROR; 2 arguments required; \nusage: python {scriptName} [HOST] [PORT]')
    
    host = sys.argv[1]
    port = sys.argv[2]

    LOG_FORMAT = '%(asctime)s.%(msecs)03dZ %(name)-10s %(levelno)s \
        %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(datefmt = "%Y-%m-%d %H:%M:%S", format = LOG_FORMAT)
    logger = logging.getLogger('trius')
    logger.setLevel(logging.DEBUG)
    logger.debug('~~~~~~starting log~~~~~~')

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_asyncTCP_client_test(host, port))
    except KeyboardInterrupt:
        print('Exiting Program...')