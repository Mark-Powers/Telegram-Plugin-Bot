import difflib

from plugin import Plugin

class BotPlugin(Plugin):
	def __init__(self, data_directory, bot):
		self.dir = data_directory
		self.bot = bot

	def on_command(self, command):
		if command.command == "plugins":
			return {"type":"message", "message": self.bot.list_plugins()}
		elif command.command == "reload":
			if self.bot.reload_plugins():
				return {"type":"message", "message": "Plugins have been reloaded!"}
			return {"type":"message", "message": "Failed to reload plugins!"}
		elif command.command == "help":
			return {"type":"message", "message": self.bot.plugin_help(command.args)}
		elif command.command == "enable":
			if self.bot.enable_plugin(command.args):
				return {"type":"message", "message": "Successfully enabled {}.".format(command.args)}
			return {"type":"message", "message": "Failed to enable {}, it may already be enabled or it does not exist!".format(command.args)}
		elif command.command == "disable":
			if self.bot.disable_plugin(command.args):
				return {"type":"message", "message": "Successfully disabled {}.".format(command.args)}
			return {"type":"message", "message": "Failed to disable {}, it may already be disabled or it does not exist!".format(command.args)}

	def get_commands(self):
		return {"plugins", "reload", "enable", "disable", "help"}

	def get_name(self):
		return "Plugin Manager"

	def get_help(self):
		return "This plugin manages general plugins"

	def has_message_access(self):
		return False

	def on_message(self, message):
		pass

	def enable(self):
		pass

	def disable(self):
		pass
