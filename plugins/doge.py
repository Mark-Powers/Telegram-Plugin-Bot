import random
from plugin import Plugin

def load(data_dir, bot):
	return Doge(data_dir, bot)

class Doge(Plugin):
	def __init__(self, data_directory, bot):
		self.dir = data_directory
		self.bot = bot
		self.parts = ["many", "very", "such", "much", "so", "wow"]
		self.words = []

	def on_command(self, command):
		if command.command == "doge":
			caption = ""
			top_words = sorted(self.words, key=len, reverse=True)[:5]
			random.shuffle(top_words)
			for word in top_words:
				choice = random.choice(self.parts)
				if choice == "wow":
					caption += choice
				else:
					caption += choice + " "+ word
				caption += "\n"
			self.words = []
			return  {"type": "photo", "caption": caption.strip(),
					"file_name": self.dir+"/doge.jpg"}

	def get_commands(self):
		return {"doge"}

	def get_name(self):
		return "Doge"

	def get_help(self):
		return "Sends doge pictures!"

	def has_message_access(self):
		return True

	def on_message(self, message):
		self.words.extend(message.text.split(" "))
		return ""
