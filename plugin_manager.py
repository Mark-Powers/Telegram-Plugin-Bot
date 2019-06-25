import importlib

from plugin import Plugin

class PluginManager:
    def __init__(self, config, bot):
        # List of Plugin python files found in the Bot's config file to be imported and loaded
        self.config_plugins = config.plugins
        # List of Plugin python files dynamically imported and loaded
        self.dynamic_plugins = []
        # Signifys if Plugin's have already been imported via Python's module lib
        self.imported = False
        # List of all Plugin objects
        self.plugins = []
        # List of all Plugins listening for messages
        self.message_plugins = []
        # Map of command strings to Plugin objects. When a command string is received, that Plugin's on_command method is run
        self.commands = {}
        # Map of all Plugin names to booleans. Plugin's that are enabled are set as True and allow their commands to be run
        self.is_enabled = {}
        # Loads Plugins listed within the configuration file
        self.load_plugins(bot)

    def load_plugins(self, bot):
        # Resets all instance variables for potential subsequent reloads
        self.plugins = []
        self.message_plugins = []
        self.commands = {}
        self.is_enabled = {}

        for plugin in self.config_plugins:
            if not self.imported:
                importlib.import_module("plugins." + plugin)
            self.plugins.append(eval("mod."+plugin+".load(\"plugins/" + plugin + "\", bot)"))
        
        self.imported = True

        for plugin in self.plugins:
            for command in plugin.get_commands():
                self.commands[command] = plugin
            if plugin.has_message_access():
                self.message_plugins.append(plugin)
            self.is_enabled[plugin.get_name()] = True

    def dynamically_load(self, bot):
        pass

    def reload_plugins(self, bot):
        self.load_plugins(bot)

    def process_plugin(self, bot, message):
        if self.is_enabled[self.commands[message.command.command].get_name()]:
            return self.commands[message.command.command].on_command(message.command)
        return {"type": "message", "message": "This command is currently disabled."}

    def process_message(self, bot, message):
        for plugin in self.message_plugins:
            if self.is_enabled[plugin.name]:
                reply = plugin.on_message(message)

                if reply:
                    bot.send_message(message.chat.id, reply)

    def enable_plugin(self, plugin_name):
        for plugin in self.plugins:
            if plugin.get_name() == plugin_name:
                if not self.is_enabled[plugin.get_name()]:
                    self.is_enabled[plugin_name] = True
                    plugin.enable()
                    return True
                return False
        return False

    def disable_plugin(self, plugin_name):
        for plugin in self.plugins:
            if plugin.get_name() == plugin_name:
                if self.is_enabled[plugin.get_name()]:
                    self.is_enabled[plugin_name] = False
                    plugin.disable()
                    return True
                return False
        return False

    def list_commands(self):
        response = "Commands:\n"

        for plugin in self.plugins:
            response += "\t" + plugin.get_name() + "\n"
            for command in plugin.get_commands():
                response += "\t\t" + command + "\n"
        return response

    def list_listeners(self):
        return "Listeners:\n"+str(self.message_plugins)
        
