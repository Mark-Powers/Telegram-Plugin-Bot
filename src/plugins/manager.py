import difflib

from plugin import Plugin

class BotPlugin(Plugin):
	def __init__(self, data_directory, bot):
		self.dir = data_directory
		self.bot = bot

	def on_command(self, command):
		if command.command == "plugins":
			return {"type":"message", "message": self.list_plugins()}
		elif command.command == "reload":
			self.bot.load_plugins()
			return {"type":"message", "message": "Plugins are reloaded!"}
		elif command.command == "help":
			matches = difflib.get_close_matches(command.args, [x.get_name() for x in self.bot.plugins])
			if matches:
				for plugin in self.bot.plugins:
					if plugin.get_name() == matches[0]:
						return {"type":"message", "message": plugin.get_help()}
			return {"type":"message", "message": "I don't know that plugin!"}

	def get_commands(self):
		return {"plugins", "reload", "help"}

	def get_name(self):
		return "Plugin Manager"

	def get_help(self):
		return "This plugin manages general plugins"

	def has_message_access(self):
		return False

	def list_plugins(self):
		string = ""
		for plugin in self.bot.plugins:
			string += ", '" + plugin.get_name()+"'"
		return string[2:]

	def on_message(self, message):
		pass

	def enable(self):
		pass

	def disable(self):
		pass
