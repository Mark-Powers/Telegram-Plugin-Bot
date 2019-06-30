import os
import random
from plugin import Plugin

class BotPlugin(Plugin):
	def __init__(self, data_dir, bot):
		self.dir = data_dir
		self.pasta = {}
		if not os.path.exists(self.dir):
			os.makedirs(self.dir)
		for file in os.listdir(self.dir):
			if file.endswith(".txt"):
				with open(self.dir+"/"+file, 'r') as f:
					self.pasta[file[:-4]] = f.read()

	def add(self, message):
		parts = message.split("\n",1)
		if len(parts) == 2 and parts[0] and parts[1]:
			file_name = parts[0] + ".txt"
			self.pasta[parts[0]] = parts[1]
			with open(self.dir+"/"+file_name, 'w') as f:
				f.write(parts[1])
			return "Created pasta '" + parts[0] + "''"
		else:
			return "Invalid syntax! Please enter pasta title on first line and begin pasta on next line"

	def get_pasta(self, message):
		if(message in self.pasta.keys()):
			return self.pasta[message]
		if len(self.pasta) > 0:
			return self.pasta[random.choice(list(self.pasta.keys()))]
		else:
			return "No pasta set!"

	def on_command(self, command):
		if command.command == "pasta":
			return {"type":"message", "message": self.get_pasta(command.args)}
		elif command.command == "listpasta":
			ret = "\n".join(list(self.pasta.keys()))
			if ret:
				return {"type":"message", "message": ret}
			else:
				 return {"type":"message", "message": "No pasta set!"}
		elif command.command == "newpasta":
			return {"type":"message", "message": self.add(command.args)}

	def get_commands(self):
		return {"pasta", "listpasta", "newpasta"}

	def get_name(self):
		return "Pasta"

	def get_help(self):
		return "/pasta <name (optional)>"

	def on_message(self, message):
		pass

	def has_message_access(self):
		return False
	
	def enable(self):
		pass

	def disable(self):
		pass