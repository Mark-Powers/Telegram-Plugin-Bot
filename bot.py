import requests
import json
from time import sleep
import random
import os
import re

from roll import Roll
from character import Character
from config import Config
from pasta import Pasta
from trigger import Trigger

config = Config("config.txt")

token = config.get_token()
bot_dir = config.get_bot_dir()
bot_username = config.get_bot_username()

url = "https://api.telegram.org/bot"+token+"/"

username_pattern = re.compile("@(\w+)")
dice_format_pattern = re.compile("\d+d\d+", re.IGNORECASE)

triggers = Trigger(bot_dir+"/triggers")
print("TRIGGERS")
print(list(triggers.get_keys()))

pasta = Pasta(bot_dir+"/pasta")
print("\nPASTA:")
print(list(pasta.get_keys()))

characters = {}
for file in os.listdir(bot_dir+"/characters"):
	if file.endswith(".txt"):
		with open(bot_dir+"/characters/"+file, 'r') as f:
			lines = f.readlines()
			char = Character(lines.pop(0).strip())
			for line in lines:
				#line = line.strip()
				if line.startswith("inventory:"):
					line = line.replace("inventory:","",1)
					for item in line.split(":"):
						if item:
							group = item.split(",")
							char.give_item(group[0], int(group[1]), group[2])
				elif "=" in line:
					parts = line.split("=")
					char.set_stat(parts[0], int(parts[1]))					
			characters[file[:-4]] = char

print("\nCHARACTERS:")
print(list(characters.keys()))	

def addTrigger(parts):


	if(len(parts) > 1):
		phrases.append(parts[0])
		phrase_responses[parts[0]] = parts[1:]
		file_name = parts[0].replace(" ", "-") + ".txt"
		with open(bot_dir+"/triggers/"+file_name, 'w') as f:
			for part in parts:
				f.write(part+"\n")

def addPasta(parts):
	if(len(parts) == 2):
		pasta[parts[0]] = parts[1]
		file_name = parts[0].replace(" ", "-") + ".txt"
		with open(bot_dir+"/pasta/"+file_name, 'w') as f:
			f.write(parts[1]+"\n")

def sendMessage(id, message):
	requests.get(url + 'sendMessage', params=dict(chat_id=id, text=message))

def sendApplause(id):
	for i in range(0,3):
		sendMessage(id, u"😎//")

def sendPasta(message, id):
	message = message.replace("/pasta ","",1) + ".txt"
	if(message in pasta.keys()):
		sendMessage(id, pasta[message])
	else:
		sendMessage(id, pasta[random.choice(list(pasta.keys()))])
	
def rollDice(user, message, id):
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
	sendMessage(id, result)

def show_stats(user, id):
	sendMessage(id, characters[user].stat_string())

def show_inventory(user, id):
	sendMessage(id, characters[user].inventory_string())

def set_stat(user, message, id):
	message = message.replace("/set_stat", "", 1).strip()
	parts = message.split(" ")
	if len(parts)==2:
		characters[user].set_stat(parts[0], int(parts[1]))
		write_char_for_username(user)
		show_stats(user, id)
	else:
		sendMessage(id, "Invalid number of arguments!")

def give_item(user, message, id):
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

def create_character(message, user, c_id):
	message = message.replace("/create_character", "", 1).strip()
	if message:
		characters[user] = Character(message)
		write_char_for_username(user)
		sendMessage(c_id, "Created character " + message + " for player " + user)
	else:
		sendMessage(c_id, "Name your character!")

def write_char_for_username(user):
	characters[user].write_to_file(bot_dir+"/characters/"+user+".txt")


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
			if message.startswith('/newtrigger'):
				parts = message.splitlines()
				parts[0] = parts[0].replace("/newtrigger ","",1)
				addTrigger(parts)
				print("New trigger: "+parts[0]+" made by "+user)
			elif message.startswith('/newpasta'):
				parts = message.split("\n",1)
				parts[0] = parts[0].replace("/newpasta ", "", 1)
				addPasta(parts)
				print("New pasta: " + parts[0]+" made by " + user)
			elif message.startswith('/listtrigger'):
				sendMessage(c_id, "\n".join(phrases))
			elif message.startswith('/listpasta'):
				response = "\n".join(pasta.keys())
				sendMessage(c_id, response.replace(".txt", ""))
			elif message.startswith('/applause'):
				sendApplause(c_id)
			elif message.startswith('/pasta'):
				sendPasta(message, c_id)
			elif message.startswith('/roll ') or message.startswith("/r "):
				rollDice(user, message, c_id)
			elif message.startswith("/create_character"):
				create_character(message, user, c_id) 
			elif message.startswith("/show_stats"):
				if("@" in message):
					user = username_pattern.search(message).group(1)
					message = message.replace(" @"+user,"",1)
				if user in characters:
					show_stats(user, c_id) 
				else:
					sendMessage(c_id, user + " does not have a character!")
			elif message.startswith("/show_inventory"):
				if("@" in message):
					user = username_pattern.search(message).group(1)
					message = message.replace(" @"+user,"",1)
				if user in characters:
					show_inventory(user, c_id) 
				else:
					sendMessage(c_id, user + " does not have a character!")
			elif message.startswith("/set_stat"):
				if("@" in message):
					user = username_pattern.search(message).group(1)
					message = message = message.replace(" @"+user,"",1)
				if user in characters:
					set_stat(user, message, c_id) 
				else:
					sendMessage(c_id, user + " does not have a character!")
			elif message.startswith("/give_item"):
				if("@" in message):
					user = username_pattern.search(message).group(1)
					message = message.replace(" @"+user,"",1)
				if user in characters:
					give_item(user, message, c_id)
				else:
					sendMessage(c_id, user + " does not have a character!")
			else: # Generic Message
				reply = triggers.parse(message)
				if reply:
					sendMessage(c_id, reply)	
	sleep(config.get_sleep_interval())
