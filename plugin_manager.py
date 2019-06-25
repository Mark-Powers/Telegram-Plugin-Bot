import importlib

from plugin import Plugin

class PluginManager:
    def __init__(self, config, bot):
        self.config_plugins = config.plugins
        self.imported = False
        self.plugins = []
        self.message_plugins = []
        self.commands = {}
        self.load_plugins(bot)

    def load_plugins(self, bot):
        self.plugins = []
        self.message_plugins = []
        self.commands = {}

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

    def process_plugin(self, bot, message):
        return self.commands[message.command.command].on_command(message.command)

    def process_message(self, bot, message):
        for plugin in self.message_plugins:
            reply = plugin.on_message(message)

            if reply:
                bot.send_message(message.chat.id, reply)

    def reload_plugins(self, bot):
        self.load_plugins(bot)

    def enable_plugin(self, plugin_name):
        pass

    def disable_plugin(self, plugin_name):
        pass

    def list_commands(self):
        response = "Commands:\n"

        for plugin in self.plugins:
            response += "\t" + plugin.get_name() + "\n"
            for command in plugin.get_commands():
                response += "\t\t" + command + "\n"
        return response

    def list_listeners(self):
        return "Listeners:\n"+str(self.message_plugins)
        
