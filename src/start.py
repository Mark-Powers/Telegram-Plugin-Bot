import logging
import os
import threading

from bot import Bot
from config import Config, ConfigWizard

class BotThread(threading.Thread):
    """
	Creates a single daemon thread running the Bot class's start method
	...

	Methods
	-------
    run()
        Runs the Bot's start() method
    stop()
        Raises stop event flag
    stopped()
        Returns true if the stop event flag has been raised
    """

    def __init__(self, bot, threadID, name):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self._stop_event = threading.Event()
        self.bot = bot
        self.name = name
        self.threadID = threadID

    def run(self):
        """
        Runs the Bot class's start() method on a separate thread
        """

        print("Starting thread with name:{}".format(self.name))
        self.bot.start(self)
        print("Stopping thread with name:{}".format(self.name))

    def stop(self):
        """
        Raises stop event flag (sets it to true)
        """

        self._stop_event.set()

    def stopped(self):
        """
        Returns true if the stop event flag has been raised (the stop method has been called)
        """

        return self._stop_event.is_set()


# Create logger
logger = logging.getLogger('bot_log')
logger.setLevel(logging.DEBUG)

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('bot.log')
c_handler.setLevel(logging.DEBUG)
f_handler.setLevel(logging.DEBUG)

# Create formatters and add to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)

logger.info('Starting up bot...')

# Setup config
if os.path.exists("config.txt"):
	conf = Config("config.txt")
else:
	conf = ConfigWizard("config.txt").conf

# Create and start the bot
bot = Bot(conf)
bot_thread1 = BotThread(bot, 0, "Start-0")
bot_thread1.start()

# Enable cli
command = ""
logger.info("Command-line enabled:")

while not command == "/quit":
    command = input()

# Close all threads
bot_thread1.stop()
bot_thread1.join()