import os
import random

class Trigger:
	def __init__(self, trigger_directory):
		self.__directory = trigger_directory
		self.__triggers = {}
		for file in os.listdir(trigger_directory):
			if file.endswith(".txt"):
				with open(trigger_directory+"/"+file, 'r') as f:
					responses = []
					for line in f.read().splitlines():
						if line:
							responses.append(line)
					self.__triggers[file[:-4]] = responses
	
	def add(self, phrase, responses):
		if phrase:
			file_name = phrase + ".txt"
			output = ""
			for responses in responses:
					if response:
						f.write(part+"\n")
			if output:
				with open(self.__directory+"/"+file_name, 'w') as f:
					f.write(output)

				

	def parse(self, message):
		for word in self.__triggers.keys():
			#word = word.lower()
			exp = r'\b'+ word + r'\b'
			#message = message.lower()
			if re.search(exp, message, re.IGNORECASE):
				return random.choice(self.__triggers[word])
		return ""

	def get_keys(self):
		return self.__triggers.keys()