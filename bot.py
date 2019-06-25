import requests
import json
import re
import time
import threading
import os
import imp

from config import Config, ConfigWizard
from command_wrappers import Command, User, Chat, Message
from plugin_manager import PluginManager

class Bot:
	def __init__(self, config):
		self.directory = config.bot_dir
		self.base_url = "https://api.telegram.org/bot"+config.token+"/"
		self.sleep_interval = config.sleep_interval
		self.username = json.loads(requests.get(self.base_url + "getMe").text)["result"]["username"]
		self.plugin_manager = PluginManager(config, self)

	def start(self):
		last_update = 0

		print(self.plugin_manager.list_commands())
		print(self.plugin_manager.list_listeners())

		while True:
			updates = self.get_updates(last_update)
			#updates = json.loads(requests.get(self.base_url + 'getUpdates', params=dict(offset=(last_update+1))).text)
			for update in updates["result"]:
				last_update = update["update_id"]

				if "message" in update:
					message = Message(update["message"])
					print(str(last_update)+": "+message.sent_from.username)

					if message.is_command:
						try:
							response = self.plugin_manager.process_plugin(self, message)

							if response["type"] == "message":
								self.send_message(message.chat.id, response["message"])
							elif response["type"] == "photo":
								self.send_photo(message.chat.id, response["caption"], response["file_name"])
						except KeyError:
							self.send_message(message.chat.id, "Invalid command!\n'" + message.command.command + "'")
						except Exception as e:
							self.send_message(message.chat.id, "I'm afraid I can't do that.\n'"+str(e)+"'")
					else:
						self.plugin_manager.process_message(self, message)
			time.sleep(self.sleep_interval)

	def get_updates(self, last_update):
		return json.loads(requests.get(self.base_url + 'getUpdates', params=dict(offset=(last_update+1))).text)

	def send_message(self, id, message):
		return requests.get(self.base_url + 'sendMessage', params=dict(chat_id=id, text=message))

	def send_photo(self, id, message, file_name):
	    files = {'photo': open(file_name, 'rb')}
	    data = dict(chat_id=id, caption=message)

	    return requests.get(self.base_url + 'sendPhoto', files=files, data=data)


if os.path.exists("config.txt"):
	conf = Config("config.txt")
else:
	conf = ConfigWizard("config.txt").conf
bot = Bot(conf)
bot.start()
