import asyncio
import os
import signal
import sys
import logging  # Import logging

from source.core.Bot import Bot
from source.utils.Console import Terminal
from source.utils.Constants import SESSION_FOLDER_PATH, RESOURCE_FILE_PATH, MEDIA_FOLDER_PATH

console = Terminal.console

# Setting logging
logging.basicConfig(
    filename='bot_activity.log',  # log file
    level=logging.INFO,  # log level
    format='%(asctime)s - %(levelname)s - %(message)s'  # message format
)

#TODO Add documentation
async def shutdown(loop, signal=None):
    if signal:
        logging.info(f"Received exit signal {signal.name}...")  # loggin receive singal
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    logging.info(f"Cancelling {len(tasks)} tasks...")  # logging
    [task.cancel() for task in tasks]

    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

def setup_directories():
    os.makedirs(RESOURCE_FILE_PATH, exist_ok=True)
    os.makedirs(MEDIA_FOLDER_PATH, exist_ok=True)
    os.makedirs(SESSION_FOLDER_PATH, exist_ok=True)

def setup_signal_handlers(loop):
    if sys.platform != 'win32':
        signals = (signal.SIGINT, signal.SIGTERM)
        for s in signals:
            loop.add_signal_handler(s, lambda a=s: asyncio.create_task(shutdown(loop, signal=s)))

def main():
    setup_directories()
    bot = Bot()
    try:
        loop = asyncio.get_event_loop()
        setup_signal_handlers(loop)
        loop.run_until_complete(bot.start())
        logging.info("Bot started successfully.")  # logging start
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        logging.error(f"Error occurred: {e}")  # error logging
    finally:
        loop.close()

if __name__ == "__main__":
    main()
