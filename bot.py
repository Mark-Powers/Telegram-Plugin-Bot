import requests
import json
from time import sleep
import random
import os
import re

bot_dir = os.path.abspath('')

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
print(phrases)

def addTrigger(parts):
	phrases.append(parts[0])
	phrase_responses[parts[0]] = parts[1:]
	file_name = parts[0].replace(" ", "-") + ".txt"
	with open(bot_dir+"/triggers/"+file_name, 'w') as f:
		for part in parts:
			f.write(part+"\n")

def findWord(w, p):
	w = w.lower()
	p = p.lower()
	exp = "".join([r'\b', w, r'\b'])
	return re.match(exp, p)

def sendMessage(id, message):
	requests.get(url + 'sendMessage', params=dict(chat_id=id, text=message))

while True:
	get_updates = json.loads(requests.get(url + 'getUpdates', params=dict(offset=(last_update+1))).text)

	for update in get_updates['result']:
		last_update = update['update_id']
		user = update['message']['from']['first_name']
		print(str(last_update)+": "+user)
		if 'message' in update and 'text' in update['message']:
			message = update['message']['text'].lower()
			c_id = update['message']['chat']['id']
			if message.startswith('/newtrigger'):
				parts = message.splitlines()
				parts[0] = parts[0].replace("/newtrigger ","",1)
				addTrigger(parts)
				print("New trigger: "+parts[0]+" made by "+user)
			elif message.startswith('/list'):
				sendMessage(c_id, "\n".join(phrases))
			else: # Generic Message
				for word in phrases:
					if findWord(word, message):
						sendMessage(c_id, random.choice(phrase_responses[word]))
						break
	# Write new last_update to file
	with open(bot_dir+"/last_update", "w") as f:
		f.write(str(last_update))

	sleep(2)

