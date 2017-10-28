from plugin import Plugin

def load(data_dir, bot):
	return Manager(data_dir, bot)

class Manager(Plugin):
	def __init__(self, data_directory, bot):
		self.dir = data_directory
		self.bot = bot

	def on_command(self, command):
		if command.command == "plugins":
			return self.list_plugins()
		elif command.command == "reload":
			self.bot.load_plugins()
			return "Plugins are reloaded!"

	def get_commands(self):
		return {"plugins", "reload"}

	def get_name(self):
		return "Pluging Manager"

	def get_help(self):
		return "This plugin manages general plugins"

	def has_message_access(self):
		return False

	def list_plugins(self):
		string = ""
		for plugin in self.bot.plugins:
			string += ", '" + plugin.get_name()
		return string[2:]+"'"
