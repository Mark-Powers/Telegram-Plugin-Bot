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
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


# Setup and configure logger

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

while not command == "/quit":
    command = input()

# Close all threads
bot_thread1.stop()
bot_thread1.join()