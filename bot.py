import requests
import json
import re
import time

from roll import Roll
from character import Character
from character import CharacterManager
from config import Config
from pasta import Pasta
from trigger import Trigger

config = Config("config.txt")

token = config.get_token()
bot_dir = config.get_bot_dir()
bot_username = config.get_bot_username()
url = "https://api.telegram.org/bot"+token+"/"

dice_format_pattern = re.compile("\d+d\d+", re.IGNORECASE)

triggers = Trigger(bot_dir+"/triggers")
print("TRIGGERS")
print(triggers.get_keys())

pasta = Pasta(bot_dir+"/pasta")
print("\nPASTA:")
print(pasta.get_keys())

char_man = CharacterManager(bot_dir+"/characters")
print("\nCHARACTERS:")
print(char_man.get_users())

def send_message(id, message):
	requests.get(url + 'sendMessage', params=dict(chat_id=id, text=message))

def add_trigger(command):
	parts = command.get_args().splitlines()
	if len(parts) > 1:
		triggers.add(parts[0], parts[1:])
		send_message(command.get_id(), "Added trigger: " + parts[0])
	else:
		send_message(command.get_id(), "Invalid syntax")

def list_trigger(command):
	send_message(command.get_id(), "\n".join(triggers.get_keys()))

def add_pasta(command):
	parts = command.get_args().split("\n",1)
	if len(parts) == 2:
		pasta.add(parts[0], parts[1])
		send_message(command.get_id(), "Added pasta: " + parts[0])
	else:
		send_message(command.get_id(), "Invalid syntax")

def list_pasta(command):
	send_message(command.get_id(), "\n".join(pasta.get_keys()))

def send_pasta(command):
	send_message(command.get_id(), pasta.get_pasta(command.get_args))

def send_applause(command):
	for i in range(0,3):
		send_message(command.get_id(), u"😎//")
	
def roll_dice(command):
	message = message.replace("/roll","",1).strip()
	message = message.replace("/r","",1).strip()
	rolls = []
	constant = []
	mods = []
	for part in message.split("+"):
		#if "d" in part: 
		if dice_format_pattern.search(part):
			rolls.append(Roll(part)) 
		elif part.isdigit(): 
			constant.append(int(part)) 
		else:
			if user in characters and part in characters[user].stats:
				mods.append(part)
	result = user + " rolled:"
	total = 0
	for roll in rolls:
		total += roll.sum()
		result += "\n(" + ", ".join(str(s) for s in roll.rolls) + ") = " + str(roll.sum())
	for mod in mods:		
		mod_value = int((characters[user].stats[mod]-10)/2)
		total += mod_value
		result += "\n + " + mod +" (" + str(mod_value) + ")"
	for c in constant:
		total += c
		result += "\n + " + str(c)
	result += "\n = " + str(total)
	send_message(id, result)

def show_stats(command):
	send_message(id, characters[user].stat_string())

def show_inventory(command):
	send_message(id, characters[user].inventory_string())

def set_stat(command):
	if("@" in message):
		user = username_pattern.search(message).group(1)
		message = message.replace(" @"+user,"",1)
	if user in characters:
		show_stats(user, c_id) 
	else:
		send_message(c_id, user + " does not have a character!")

	message = message.replace("/set_stat", "", 1).strip()
	parts = message.split(" ")
	if len(parts)==2:
		characters[user].set_stat(parts[0], int(parts[1]))
		write_char_for_username(user)
		show_stats(user, id)
	else:
		send_message(id, "Invalid number of arguments!")

def give_item(command):
	message = message.replace("/give_item", "", 1).strip()
	parts = message.split(" ", 2)
	print(parts)
	item = parts[0]
	amount = 1
	desc = "no description"
	if len(parts) > 1 and parts[1].isdigit():
		amount = int(parts[1])
	if len(parts) > 2:
		desc = parts[2]
	characters[user].give_item(item, amount, desc)
	write_char_for_username(user)
	show_inventory(user, id)

def create_character(command):
	message = message.replace("/create_character", "", 1).strip()
	if message:
		characters[user] = Character(message)
		write_char_for_username(user)
		send_message(c_id, "Created character " + message + " for player " + user)
	else:
		send_message(c_id, "Name your character!")

def write_char_for_username(user):
	characters[user].write_to_file(bot_dir+"/characters/"+user+".txt")

class Command:
	def __init__(self, sender, message, id):
		message = message.strip()
		if " " in message:
			args_index = message.index(" ")
		else:
			args_index = len(message)
		self.command = message[:args_index]
		message = message[args_index+1:]

		user_match = re.search("@(\w+)", message)
		if user_match:
			self.mention = user_match.group(1)
		else:
			self.mention = ""
		message = message.replace("@"+user,"",1).strip()
		self.args = message
		self.sender = sender
		self.id = id

	def get_sender(self):
		return self.sender

	def get_id(self):
		return self.id

	def get_command(self):
		return self.command

	def get_mention(self):
		return self.mention

	def get_args(self):
		return self.args

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

last_update = 0
while True:
	get_updates = json.loads(requests.get(url + 'getUpdates', params=dict(offset=(last_update+1))).text)

	for update in get_updates['result']:
		last_update = update['update_id']
		if 'message' in update and 'text' in update['message']:
			try:
				user = update['message']['from']['username']
			except:
				user = str(update['message']['from']['id'])
			print(str(last_update)+": "+user)
			message = update['message']['text']
			message = message.replace("@"+bot_username, "")
			c_id = update['message']['chat']['id']
			if message.startswith("/"): # Message is a command
				command = Command(user, message, c_id)
				print(command.get_command() + "->" + command.get_args())
				if command.get_command() in commands:
					commands[command.get_command()](command)
			else: # Message is normal
				reply = triggers.parse(message)
				if reply:
					send_message(c_id, reply)	
	time.sleep(config.get_sleep_interval())
