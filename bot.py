import requests
import json
import re
import time
import threading
import os
import imp

from config import Config
from plugin import Plugin

class Bot:
	def __init__(self, config):
		self.directory = config.bot_dir
		self.base_url = "https://api.telegram.org/bot"+config.token+"/"
		self.sleep_interval = config.sleep_interval

		self.username = json.loads(requests.get(self.base_url + "getMe").text)["result"]["username"]

		self.conf_plugins = config.plugins
		self.load_plugins()

	def load_plugins(self):
		self.plugins = []
		for plugin in self.conf_plugins:
			mod = __import__("plugins." + plugin)
			self.plugins.append(eval("mod."+plugin+".load(\"plugins/" + plugin + "\", self)"))

	def start(self):
		last_update = 0
		commands = {} # Map of "command" to Plugin
		message_plugins = []
		for plugin in self.plugins:
			for command in plugin.get_commands():
				commands[command] = plugin
			if plugin.has_message_access():
				message_plugins.append(plugin)
		print("Commands:\n"+str(list(commands.keys())))
		print("Listeners:\n"+str(message_plugins))
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
							response = commands[message.command.command].on_command(message.command)
							self.send_message(message.chat.id, response)
						except KeyError:
							self.send_message(message.chat.id, "Invalid command!\n'" + message.command.command + "'")
						except Exception as e:
							self.send_message(message.chat.id, "I'm afraid I can't do that.\n'"+str(e)+"'")
					else:
						for plugin in message_plugins:
							reply = plugin.on_message(message)
							if reply:
								self.send_message(message.chat.id, reply)
			time.sleep(self.sleep_interval)

	def get_updates(self, last_update):
		return json.loads(requests.get(self.base_url + 'getUpdates', params=dict(offset=(last_update+1))).text)

	def send_message(self, id, message):
		return requests.get(self.base_url + 'sendMessage', params=dict(chat_id=id, text=message))

class Command:
	def __init__(self, message):
		text = message.text[1:]
		args_index = text.index(" ") if " " in text else len(text)
		self.command = text[:args_index]
		text = text[args_index+1:]

		user_match = re.search("@(\w+)", text)
		self.mention = user_match.group(1) if user_match else ""

		#text = text.replace("@"+user,"",1).strip()
		self.args = text.strip()

		self.chat = message.chat
		self.user = message.sent_from

class User:
	def __init__(self, user):
		self.id = user["id"]
		self.first_name = user["first_name"]
		self.username = user["username"] if "username" in user else self.first_name

class Chat:
	def __init__(self, chat):
		self.id = chat["id"]
		self.type = chat["type"]

class Message:
	def __init__(self, message):
		self.date = message["date"]
		self.sent_from = User(message["from"])
		self.chat = Chat(message["chat"])
		self.text = message["text"].strip() if "text" in message else ""
		self.is_command = self.text.startswith("/")
		if self.is_command:
			self.command = Command(self)

bot = Bot(Config("config.txt"))
bot.start()
