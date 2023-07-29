import argparse
import asyncio
import logging
import shlex
import sys

from camGUI import camGUI_App

LOGNAME = 'trius'

def custom_except_hook(loop, context):
    logger = logging.getLogger(LOGNAME)
    logger.setLevel(logging.WARNING)
    logger.warning(context['message'])
    # if "Task was destroyed" in repr(context['message']):
    #     logger.warning('Exiting Program...')

async def runTriusCam(loop, opts):
    logging.basicConfig(datefmt = "%Y-%m-%d %H:%M:%S",
                        format = '%(asctime)s.%(msecs)03dZ ' \
                                '%(name)-10s %(levelno)s ' \
                                '%(filename)s:%(lineno)d %(message)s')
    logName = LOGNAME
    logger = logging.getLogger(logName)
    logger.setLevel(opts.logLevel)
    logger.debug('~~~~~~starting log~~~~~~')

    qIn = asyncio.Queue(maxsize=10)     # Incoming data queue
    qOut = asyncio.Queue(maxsize=10)    # Outgoing data queue

    tasks = [
        asyncio.create_task(camGUI_App(logName, qIn, qOut).exec())
        ]
    taskGroup = asyncio.gather(*tasks)
    try:
        await taskGroup
    except Exception as e:
        logger.setLevel(logging.WARNING)
        logger.warn(f'Exception: {e}\nExiting Program...')
        for task in tasks:
            task.cancel()

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