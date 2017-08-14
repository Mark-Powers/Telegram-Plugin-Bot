import os
import random

class Pasta:
	def __init__(self, pasta_directory):
		self.__directory = pasta_directory
		self.__pasta = {}
		for file in os.listdir(pasta_directory):
			if file.endswith(".txt"):
				with open(pasta_directory+"/"+file, 'r') as f:
					self.__pasta[file[:-4]] = f.read()
	
	def add(self, name, pasta):
		if name and pasta:
			file_name = name + ".txt"
			if output:
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