import random
from plugin import Plugin

def load(data_dir, bot):
	return Dad(data_dir, bot)

class Dad(Plugin):
	def __init__(self, data_directory, bot):
		self.dir = data_directory
		self.bot = bot

	def get_name(self):
		return "Dad"

	def get_help(self):
		return "I'm dad!"

	def has_message_access(self):
		return True

	def on_message(self, message):
		if message.text.lower().startswith("i'm "):
			return "Hi " + message.text[4:].strip() + ", I'm dad!"
		if message.text.lower().startswith("im "):
			return "Hi " + message.text[3:].strip() + ", I'm dad!"
		return
