import os
import random
from plugin import Plugin

def load(data_dir):
	return Pasta(data_dir)

class Pasta(Plugin):
	def __init__(self, data_dir):
		self.dir = data_dir
		self.__pasta = {}
		if not os.path.exists(self.dir):
			os.makedirs(self.dir)
		for file in os.listdir(self.dir):
			if file.endswith(".txt"):
				with open(self.dir+"/"+file, 'r') as f:
					self.__pasta[file[:-4]] = f.read()

	def add(self, name, pasta):
		if name and pasta:
			file_name = name + ".txt"
			self.__pasta[name] = pasta
			with open(self.dir+"/"+file_name, 'w') as f:
				f.write(pasta)

	def get_pasta(self, message):
		if(message in self.__pasta.keys()):
			return self.__pasta[message]
		if len(self.__pasta) > 0:
			return self.__pasta[random.choice(list(self.__pasta.keys()))]
		else:
			return "No pasta set!"

	def get_keys(self):
		return list(self.__pasta.keys())

	def on_command(self, command):
		return "PASTA"

	def get_commands(self):
		return {"pasta", "listpasta"}

	def get_name(self):
		return "Pasta"

	def get_help(self):
		return "/pasta <name (optional)>"
