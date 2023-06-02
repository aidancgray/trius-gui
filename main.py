import argparse
import asyncio
import logging
import shlex
import sys

import camGUI
from asyncTCP_client import asyncTCP_client
from camGUI import camGUI_App

def custom_except_hook(loop, context):
    logger = logging.getLogger('fodo')
    logger.setLevel(logging.WARN)
    
    if repr(context['exception']) == 'SystemExit()':
        logger.debug('Exiting Program...')

async def runTriusCam(loop, opts):
    logging.basicConfig(datefmt = "%Y-%m-%d %H:%M:%S",
                        format = '%(asctime)s.%(msecs)03dZ ' \
                                '%(name)-10s %(levelno)s ' \
                                '%(filename)s:%(lineno)d %(message)s')
    
    logger = logging.getLogger('trius')
    logger.setLevel(opts.logLevel)
    logger.debug('~~~~~~starting log~~~~~~')
    host = '172.16.1.127'
    port = 9999

    inQ = asyncio.Queue()   # Incoming data queue
    outQ = asyncio.Queue()  # Outgoing data queue
    tcpClient = asyncTCP_client(host, port, inQ, outQ)
    triusGUI = camGUI_App(inQ, outQ)

    await asyncio.gather(tcpClient.tcp_echo_client(),
                         triusGUI().exec()
                         )

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if isinstance(argv, str):
        argv = shlex.split(argv)

    parser = argparse.ArgumentParser(sys.argv[0])
    parser.add_argument('--logLevel', type=int, default=logging.INFO,
                        help='logging threshold. 10=debug, 20=info, 30=warn')

    opts = parser.parse_args(argv)
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(custom_except_hook)
    try:
        loop.run_until_complete(runTriusCam(loop, opts))
    except KeyboardInterrupt:
        print('Exiting Program...')
    finally:
        loop.close()
        asyncio.set_event_loop(None)

if __name__ == "__main__":
    main()