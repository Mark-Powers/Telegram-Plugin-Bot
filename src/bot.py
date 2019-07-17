import logging
import requests
import json
import re
import time
import threading
import os

from command_wrappers import Command, User, Chat, Message
from plugin_manager import PluginManager

class Bot:
	"""
	Singleton Bot class that acts as the controller for messages received and sent to Telegram.
	This file should be run when starting the bot currently.

	...

	Methods
	-------
	start()
		Starts the bot where it will check for updates received from Telegram and send replies based on Plugins and Messages.

	reload_plugins()
		Reloads all plugins managed in self.plugin_manager, incorporating new changes made

	enable_plugin(plugin_name)
		Enables a plugin with a specific name

	disable_plugin(plugin_name)
		Disables a plugin with a specific name

	plugin_help(plugin_name)
		Returns a string containing the help message from a Plugin's get_help method

	list_plugins()
		Returns a str listing all plugins

	get_updates(last_update)
		Gets message updates from Telegram based on those last received.

	send_message(id, message)
		Sends a message to Telegram.

	send_photo(id, message, file_name)
		Sends a photo to Telegram.
	"""

	def __init__(self, config):
		"""
		Sets up initial bot data and the PluginManager which loads inital plugins.
		...

		Parameters
		----------
		config: Config
			Configuration object containing data found within the bot's configuration file.
		"""

		self.logger = logging.getLogger('bot_log')
		self.directory = config.bot_dir
		self.base_url = "https://api.telegram.org/bot"+config.token+"/"
		self.sleep_interval = config.sleep_interval
		self.username = json.loads(requests.get(self.base_url + "getMe").text)["result"]["username"]
		self.plugin_manager = PluginManager(config, self)

		print(self.plugin_manager.list_commands())
		print(self.plugin_manager.list_listeners())

	def start(self, thread):
		"""
		Receives and sends messages to Telegram forever.
		Responses made by the bot are based on functionality contained within Plugins.
		"""

		self.logger.info("Starting telegram update loop")
		last_update = 0

		while not thread.stopped():
			updates = self.get_updates(last_update)

			for update in updates["result"]:
				last_update = update["update_id"]

				if "message" in update:
					message = Message(update["message"])
					print(str(last_update)+": "+message.sent_from.username)

					if message.is_command:
						self.logger.info("Command received, processing plugins")
						# Disabled threading for commands, need to implement locking synch for processing plugins due to ambiguous local data
						self.plugin_manager.process_plugin, (self, message)
					else:
						threading._start_new_thread(self.plugin_manager.process_message, (self, message))
			time.sleep(self.sleep_interval)
		self.logger.warn("Ending telegram update loop due to thread manually being killed")

	def reload_plugins(self):
		"""
		Reloads all plugins managed in self.plugin_manager, incorporating new changes made
		"""

		self.plugin_manager.reload_plugins(self)
		return True

	def enable_plugin(self, plugin_name):
		"""
		Enables a plugin with a specific name
		"""

		self.logger.info("Attempting to enable plugin with name {}".format(plugin_name))
		return self.plugin_manager.enable_plugin(plugin_name)

	def disable_plugin(self, plugin_name):
		"""
		Disables a plugin with a specific name
		"""

		self.logger.info("Attempting to disable plugin with name {}".format(plugin_name))
		return self.plugin_manager.disable_plugin(plugin_name)

	def plugin_help(self, plugin_name):
		"""
		Returns a string containing the help message from a Plugin's get_help method
		"""

		self.logger.info("Requested help message from plugin with name {}".format(plugin_name))
		return self.plugin_manager.plugin_help(plugin_name)

	def list_plugins(self):
		"""
		Returns a str listing all plugins
		"""

		self.logger.info("Request recieved to list all plugins")
		return self.plugin_manager.list_plugins()

	def get_updates(self, last_update):
		"""
		Gets message updates from Telegram based on those last received.

		...

		Parameters
		----------
		last_update: json
			Data received from telegram dictating new messages that were send/visible to the bot.
		"""

		return json.loads(requests.get(self.base_url + 'getUpdates', params=dict(offset=(last_update+1))).text)

	def send_message(self, id, message):
		"""
		Sends a string message to a specific telegram chatroom containing the designated id.

		...

		Parameters
		----------
		id: str
			The id of the chatroom to send a message to.

		message: str
			The message to be send to a chatroom.
		"""

		self.logger.info("Sending message ({}) to channel with id {}".format(message, id))
		return requests.get(self.base_url + 'sendMessage', params=dict(chat_id=id, text=message))

	def send_photo(self, id, message, file_name):
		"""
		Sends a photo found with the designated filename with an optional caption string message to a chatroom containing the designated id

		...

		Parameters
		----------
		id: str
			The id of the chatroom to send a message to.

		message: optional
			An optional string to send with an image as a caption

		file_name: str
			The filename of the photo to send to a Telegram chatroom
		"""

		files = {'photo': open(file_name, 'rb')}
		data = dict(chat_id=id, caption=message)

		self.logger.info("Sending photo with caption ({}) with filename ({}) to channel with id {}".format(message, file_name, id))
		return requests.get(self.base_url + 'sendPhoto', files=files, data=data)

