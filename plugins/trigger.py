import os
import random
import re
from plugin import Plugin

def load(data_dir):
	return Trigger(data_dir)

class Trigger(Plugin):
	def __init__(self, trigger_directory):
		self.dir = trigger_directory
		self.triggers = {}
		if not os.path.exists(self.dir):
			os.makedirs(self.dir)
		for file in os.listdir(self.dir):
			if file.endswith(".txt"):
				with open(self.dir+"/"+file, 'r') as f:
					responses = []
					for line in f.read().splitlines():
						if line:
							responses.append(line)
					self.triggers[file[:-4]] = responses

	def on_message(self, message):
		for word in self.triggers.keys():
			#word = word.lower()
			exp = r'\b'+ word + r'\b'
			#message = message.lower()
			if re.search(exp, message.text, re.IGNORECASE):
				return random.choice(self.triggers[word])
		return ""

	def on_command(self, command):
		if command.command == "newtrigger":
			return self.add(command)
		elif command.command == "listtrigger":
			ret = "\n".join(list(self.triggers.keys()))
			return ret if ret else "No triggers set!"

	def get_commands(self):
		return {"newtrigger", "listtrigger"}

	def get_name(self):
		return "Trigger!"

	def get_help(self):
		return "This plugin has no help set"

	def has_message_access(self):
		return True

	def add(self, command):
		parts = command.args.splitlines()
		if len(parts) > 1 and parts[0]:
			file_name = parts[0] + ".txt"
			output = ""
			final_responses = []
			for response in parts[1:]:
					if response:
						output += response +"\n"
						final_responses.append(response)
			if output:
				self.triggers[ parts[0]] = final_responses
				with open(self.dir+"/"+file_name, 'w') as f:
					f.write(output)
				return "Added trigger: " + parts[0]
			else:
				return "Must have at least one valid response"
		else:
			return "Invalid syntax"
