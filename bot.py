import requests
import json
from time import sleep
import random
import os
import re

bot_dir = "/root/cafe-mod-bot"#os.path.abspath('')

# Set token from file
token = ""
try:
	token = re.search("token=\"(.+)\"", open(bot_dir+"/token").read()).group(1)
except:
	raise Exception("Incorrect file '" + bot_dir + "/token'. Requires 'token=\"<token here>\"'")

url = 'https://api.telegram.org/bot%s/' % token

# Set last_update from file
last_update = 0
try:
	last_update = int(open(bot_dir+"/last_update").read())
except:
	pass

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
	if file.endswith(".txt."):
		with open(bot_dir+"/pasta/"+file, 'r') as f:
			

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
	return re.match(exp, p)

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
		

def rollDice(message, id):
	message = message.replace("/roll ","",1)
	message = message.replace("/r ","",1)
	rolls = []
	mods = []
	for part in message.split("+"):
		if "d" in part: 
			rolls.append(Roll(part)) 
		else: 
			mods.append(int(part)) 
	result = "You rolled:"
	total = 0
	for roll in rolls:
		total += roll.sum()
		result += "\n(" + ", ".join(str(s) for s in roll.rolls) + ") = " + str(roll.sum())
	for mod in mods:
		total += mod
		result += "\n + " + str(mod)
	result += "\n = " + str(total)
	sendMessage(id, result)

class Character:
	def __init__(self, name):
		self.name = name
		self.inventory = {}
		self.stats = {}

	def give_item(item, desc, amount):
		if item in self.inventory:
			self.inventory[item][1] += amount
		else:
			self.inventory[item] = (desc, amount)
	
	def set_stat(stat, num):
		self.stats[stat] = num


def roll_stat(stat, user, id):
	characters{"user"

while True:
	get_updates = json.loads(requests.get(url + 'getUpdates', params=dict(offset=(last_update+1))).text)

	for update in get_updates['result']:
		last_update = update['update_id']
		if 'message' in update and 'text' in update['message']:
			user = update['message']['from']['username']
			print(str(last_update)+": "+user)
			message = update['message']['text'].lower()
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
			elif message.startswith('/roll') or message.startswith("/r"):
				rollDice(message, c_id)
			elif message.startswith("/create_character"):
				createCharacter(message, username, c_id) 
			else: # Generic Message
				for word in phrases:
					if findWord(word, message):
						sendMessage(c_id, random.choice(phrase_responses[word]))
						break
	# Write new last_update to file
	with open(bot_dir+"/last_update", "w") as f:
		f.write(str(last_update))

	sleep(2)

