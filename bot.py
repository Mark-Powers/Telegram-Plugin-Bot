import requests
import json
from time import sleep
import random
import os
import re

bot_dir = "/root/cafe-mod-bot"#os.path.abspath('')
bot_username = "cafe_mod_bot"

# Set token from file
token = ""
try:
	token = re.search("token=\"(.+)\"", open(bot_dir+"/token").read()).group(1)
except:
	raise Exception("Incorrect file '" + bot_dir + "/token'. Requires 'token=\"<token here>\"'")

url = 'https://api.telegram.org/bot%s/' % token

username_pattern = re.compile("@(\w+)")
dice_format_pattern = re.compile("\d+d\d+")

# Set last_update from file
last_update = 0
try:
	last_update = int(open(bot_dir+"/last_update").read())
except:
	pass


class Roll:
	def __init__(self, init_string):
		parts = init_string.split("d")
		self.num = int(parts[0])
		if(self.num < 1):
			self.num = 1
		self.size = int(parts[1])
		if(self.size < 1):
			self.size = 1
		self.rolls = []
		self.roll()

	def roll(self):
		if self.rolls:
			return self.rolls
		for i in range(self.num):
			self.rolls.append(random.randint(1, self.size))
		return self.rolls

	def sum(self):
		return sum(self.rolls)

class Character:
	def __init__(self, name):
		self.name = name
		self.inventory = {}
		self.stats = {}

	def give_item(self, item, amount, desc):
		if item in self.inventory:
			self.inventory[item] = (desc, self.inventory[item][1]+amount)
		else:
			self.inventory[item] = (desc, amount)
	
	def set_stat(self, stat, num):
		self.stats[stat] = num

	def stat_string(self):
		result = self.name + ":"
		for stat in self.stats.keys():
			result += "\n" + stat + ": " + str(self.stats[stat])
		return result
	
	def inventory_string(self):
		result = self.name + ":"
		for item in self.inventory.keys():
			result += "\n" + item + " (x" + str(self.inventory[item][1]) + ") - " + self.inventory[item][0]
		return result

	def write_to_file(self, file_name):
		output = self.name
		for stat in self.stats.keys():
			output += "\n"+stat+"="+str(self.stats[stat])
		output += "\ninventory"
		for item in self.inventory.keys():
			output+= ":" + item+","+self.inventory[item][1]+","+str(self.inventory[item][0])

		with open(file_name, 'w') as f:
			f.write(output)





# Parse existing triggers
phrases = []
phrase_responses = {}
for file in os.listdir(bot_dir+"/triggers"):
	if file.endswith(".txt"):
		with open(bot_dir+"/triggers/"+file, 'r') as f:
			phrases.append(f.readline().rstrip("\n"))
			phrase_responses[phrases[-1]] = f.read().splitlines()
			if not phrase_responses[phrases[-1]][-1]:
				phrase_responses[phrases[-1]].pop()
print("TRIGGERS")
print(phrases)

# Parse existing pasta
pasta = {}
for file in os.listdir(bot_dir+"/pasta"):
	if file.endswith(".txt"):
		with open(bot_dir+"/pasta/"+file, 'r') as f:
			pasta[file] = f.read()
print("\nPASTA:")
print(list(pasta.keys()))


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

def findWord(w, p):
	w = w.lower()
	p = p.lower()
	exp = "".join([r'\b', w, r'\b'])
	return re.search(exp, p)

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
	message = message.replace("/give_itemx ", "", 1).strip()
	parts = message.split(" ", 2)
	print(parts)
	item = parts[0]
	amount = 1
	desc = ""
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
				for word in phrases:
					if findWord(word, message):
						sendMessage(c_id, random.choice(phrase_responses[word]))
						break
	# Write new last_update to file
	with open(bot_dir+"/last_update", "w") as f:
		f.write(str(last_update))

	sleep(2)

