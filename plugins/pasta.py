import os
import random
from plugin import Plugin

def load():
	return Pasta()

class Pasta(Plugin):
	def __init__(self):
		self.__pasta = {}
		if not os.path.exists("pasta"):
			os.makedirs("pasta")
		for file in os.listdir("pasta"):
			if file.endswith(".txt"):
				with open("pasta"+"/"+file, 'r') as f:
					self.__pasta[file[:-4]] = f.read()

	def add(self, name, pasta):
		if name and pasta:
			file_name = name + ".txt"
			self.__pasta[name] = pasta
			with open(self.__directory+"/"+file_name, 'w') as f:
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

	def on_command(command):
		return "PASTA"

	def get_commands(self):
		return ["pasta", "listpasta"]

	def get_name(self):
		return "Pasta"

	def get_help(self):
		return "/pasta <name (optional)>"
