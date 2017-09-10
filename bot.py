import requests
import json
import re
import time
import threading
import os
import imp

from roll import Roll
from character import Character
from character import CharacterManager
from config import Config
from trigger import Trigger
from plugin import Plugin


class Bot:
	def __init__(self, config):
		self.username = config.get_bot_username()
		self.directory = config.get_bot_dir()
		self.base_url = "https://api.telegram.org/bot"+config.get_token()+"/"
		self.sleep_interval = config.get_sleep_interval()

		self.plugins = []
		for plugin in config.get_plugins():
			mod = __import__("plugins." + plugin)
			self.plugins.append(eval("mod."+plugin+".load(\"plugins/" + plugin + "\")"))

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
							print(commands.keys())
							print(message.command.command)
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

bot = Bot(Config("config.txt"))

dice_format_pattern = re.compile("\d+d\d+", re.IGNORECASE)

# triggers = Trigger(bot_dir+"/triggers")
# print("TRIGGERS")
# print(triggers.get_keys())
#
# pasta = Pasta(bot_dir+"/pasta")
# print("\nPASTA:")
# print(pasta.get_keys())
#
# char_man = CharacterManager(bot_dir+"/characters")
# print("\nCHARACTERS:")
# print(char_man.get_users())

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

def add_pasta(command):
	parts = command.get_args().split("\n",1)
	if len(parts) == 2:
		pasta.add(parts[0], parts[1])
		send_message(command.get_id(), "Added pasta: " + parts[0])
	else:
		send_message(command.get_id(), "Invalid syntax")

def list_pasta(command):
	if pasta.get_keys():
		send_message(command.get_id(), "\n".join(pasta.get_keys()))
	else:
		send_message(command.get_id(), "No pasta set!")

def send_pasta(command):
	send_message(command.get_id(), pasta.get_pasta(command.get_args))

def send_applause(command):
	for i in range(0,3):
		send_message(command.get_id(), u"😎//")

def roll_dice(command):
	user = command.get_sender()
	if command.get_mention():
		user = command.get_mention()
	rolls = []
	constant = []
	mods = []
	parts = command.get_args().split("+")
	for part in parts:
		if "-" in part:
			try:
				index = part.index("-",1)
				new_part = part[index:]
				part = part[:index]
				parts.append(new_part)
			except:
				pass # part is just a plain negative number
		part = part.strip()
		if dice_format_pattern.search(part):
			rolls.append(Roll(part))
		elif part.replace("-","",1).isdigit():
			constant.append(int(part))
		else:
			if char_man.has_character(user) and part in char_man.get_character(user).stats:
				mods.append(part)
	result = user + " rolled:"
	total = 0
	for roll in rolls:
		total += roll.sum()
		result += "\n(" + ", ".join(str(s) for s in roll.rolls) + ") = " + str(roll.sum())
	for mod in mods:
		mod_value = int((char_man.get_character(user).stats[mod]-10)/2)
		total += mod_value
		result += "\n + " + mod +" (" + str(mod_value) + ")"
	for c in constant:
		total += c
		result += "\n + " + str(c)
	result += "\n = " + str(total)
	send_message(command.get_id(), result)

def show_stats(command):
	user = command.get_sender()
	if command.get_mention():
		user = command.get_mention()
	if char_man.has_character(user):
		send_message(command.get_id(), char_man.get_character(user).stat_string())
	else:
		send_message(command.get_id(), user + " does not have a character!")

def show_inventory(command):
	user = command.get_sender()
	if command.get_mention():
		user = command.get_mention()
	if char_man.has_character(user):
		send_message(command.get_id(), char_man.get_character(user).inventory_string())
	else:
		send_message(command.get_id(), user + " does not have a character!")

def set_stat(command):
	user = command.get_sender()
	if command.get_mention():
		user = command.get_mention()
	if char_man.has_character(user):
		# TODO could stats be multiple words?
		parts = command.get_args().split(" ")
		if len(parts)==2:
			char_man.get_character(user).set_stat(parts[0], int(parts[1]))
			char_man.save_char(user)
			show_stats(command)
		else:
			send_message(command.get_id(), "Invalid syntax arguments!")
	else:
		send_message(command.get_id(), user + " does not have a character!")

def give_item(command):
	user = command.get_sender()
	if command.get_mention():
		user = command.get_mention()
	if char_man.has_character(user):
		if command.get_args():
			parts = command.get_args().split("|")
			item = parts[0].strip()
			amount = 1
			desc = "no description"
			if len(parts) > 1 and parts[1].strip().isdigit():
				amount = int(parts[1].strip())
			if len(parts) > 2:
				desc = parts[2].strip()
			char_man.get_character(user).give_item(item, amount, desc)
			char_man.save_char(user)
			show_inventory(command)
		else:
			send_message(command.get_id(), "Requires at least one argument!")
	else:
		send_message(command.get_id(), user + " does not have a character!")

def create_character(command):
	if message.get_args():
		char_man.add_character(message.get_sender(), Character(message))
		char_man.save_char(message.get_sender())
		send_message(c_id, "Created character '" + message.get_args() + "'' for player " + user)
	else:
		send_message(c_id, "Name your character!")

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
	"/newpasta": add_pasta,
	"/listtrigger": list_trigger,
	"/listpasta": list_pasta,
	"/applause": send_applause,
	"/pasta": send_pasta,
	"/r": roll_dice,
	"/roll": roll_dice,
	"/create_character": create_character,
	"/show_stats": show_stats,
	"/show_inventory": show_inventory,
	"/set_stat": set_stat,
	"/give_item": give_item
}

bot.start()
