import requests
import json
import re
import time
import threading
import os
import imp

from config import Config
from trigger import Trigger
from plugin import Plugin

class Bot:
	def __init__(self, config):
		self.username = config.bot_username
		self.directory = config.bot_dir
		self.base_url = "https://api.telegram.org/bot"+config.token+"/"
		self.sleep_interval = config.sleep_interval

		self.plugins = []
		for plugin in config.plugins:
			mod = __import__("plugins." + plugin)
			self.plugins.append(eval("mod."+plugin+".load(\"plugins/" + plugin + "\")"))
		print(self.plugins)

	def start(self):
		last_update = 0
		commands = {} # Map of "command" to Plugin
		for plugin in self.plugins:
			for command in plugin.get_commands():
				commands[command] = plugin

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
					elif message.text.startswith("silence"):
						if "reply_to_message" in update['message']:
							reply = update['message']["reply_to_message"]
							u_id = reply["from"]["id"]
							name = reply["from"]["first_name"]
							timeout_member(c_id, u_id, name, 5)
					else: # Message is normal
						reply = ""#triggers.parse(message)
						continue
						if reply:
							self.send_message(message.chat.id, reply)
			time.sleep(self.sleep_interval)

	def get_updates(self, last_update):
		return json.loads(requests.get(self.base_url + 'getUpdates', params=dict(offset=(last_update+1))).text)

	def send_message(self, id, message):
		requests.get(self.base_url + 'sendMessage', params=dict(chat_id=id, text=message))

# triggers = Trigger(bot_dir+"/triggers")
# print("TRIGGERS")
# print(triggers.get_keys())

def restrict_chat_member(id, u_id, name, state):
	reply = requests.get(url + "restrictChatMember", params=dict(chat_id=id, user_id=u_id, can_send_messages=state))
	if reply.ok:
		if state:
			send_message(id, name + " can talk again.")
		else:
			send_message(id, name + " has been silenced!")
	else:
		send_message(id, "I'm afraid I can't do that.\n" + str(reply.status_code))

def timeout_member(id, u_id, name, minutes):
	restrict_chat_member(id, u_id, name, False)
	t = threading.Timer(minutes*60, restrict_chat_member, [id, u_id, name, True])
	t.start()

def add_trigger(command):
	parts = command.get_args().splitlines()
	if len(parts) > 1 and triggers.add(parts[0], parts[1:]):
		send_message(command.get_id(), "Added trigger: " + parts[0])
	else:
		send_message(command.get_id(), "Invalid syntax")

def list_trigger(command):
	if triggers.get_keys():
		send_message(command.get_id(), "\n".join(triggers.get_keys()))
	else:
		send_message(command.get_id(), "No triggers set!")

def send_applause(command):
	for i in range(0,3):
		send_message(command.get_id(), u"😎//")

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

commands = {
	"/newtrigger": add_trigger,
	"/listtrigger": list_trigger,
	"/applause": send_applause,
}

bot = Bot(Config("config.txt"))

bot.start()
