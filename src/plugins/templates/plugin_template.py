from plugin import Plugin

# Name the class the name of your plugin
class BotPlugin(Plugin):
    def __init__(self, data_dir, bot):
        self.dir = data_dir
        self.bot = bot

    def on_message(self, message):
        # Implement this if has_message_access returns True
        # message is some string sent in Telegram
        # return a response to the message
        return ""

    def on_command(self, command):
        # This method is called when someone types a '/' and one of the commands returned from the set within the get_commands method in this class
        # command is a Command object found within command_wrappers.py
        if command.command == "command":
            return {"type":"message", "message": "This is a demo plugin"}

    def get_commands(self):
        # Must return a set of command strings
        return {"command"}

    def get_name(self):
        # This should return the name of your plugin, perferably the same name as this class
        return "PluginName"

    def get_help(self):
        return "Help string here!"

    def has_message_access(self):
        return False
	
    def enable(self):
        pass

    def disable(self):
        pass