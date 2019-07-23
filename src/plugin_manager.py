import logging
import importlib
import os
import threading

from plugin import Plugin

class PluginManager:
    """
    Class utilized to manage all Plugin objects loaded onto the bot.
    Features functionality to load, dynamically load, reload, enable, and disable plugins.
    Manages plugin on_command and on_message functionality when receiving messages and command strings

    ...

    Methods
    -------
    load_plugins(bot)

    dynamically_load(bot)

    reload_plugins(bot)

    process_plugin(bot, message)

    process_message(bot, message)

    enable_plugin(plugin_name)

    disable_plugin(plugin_name)

    list_commands()

    list_listeners()

    plugin_help(plugin_name)

    list_plugins()
        Returns a str listing all plugins
    """

    def __init__(self, config, bot):
        """
        Main method that setup data structures, and loads and initalizes Plugins

        ...

        Parameters
        ----------
        config: Config
            Configuration object detailing info designated within the config file

        bot: Bot
            The main Bot object responsible for sending and receiving messages
        """

        # Reference to custom logger
        self.logger = logging.getLogger('bot_log')
        # Reference to thread lock
        self.lock = threading.Lock()
        # List str of Plugin python files found in the Bot's config file to be imported and loaded
        self.config_plugins = config.plugins
        # List str of Plugin python files dynamically imported and loaded
        self.dynamic_plugins = []
        # List of imported modules
        self.modules = []
        # Bool signifys if all currently availale Plugins have been imported via Python's module lib
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
        """
        Resets instance variables, imports plugins, and initalizes them to lists and maps.
        Plugins are initially set within self.is_enabled to True, using their name as a key.
        self.imported is set to True to ensure future reloads don't attempt to reimport python files.
        After being loaded plugins are organized within self.commands and self.message_plugins based on functionality.

        ...

        Parameters
        ----------
        bot: Bot
            The main Bot object responsible for sending and receiving messages
        """

        # Resets all instance variables for potential subsequent reloads
        self.plugins = []
        self.message_plugins = []
        self.commands = {}
        self.is_enabled = {}

        self.logger.info("Attempting to load plugins...")

        if not self.imported:
            for plugin in self.config_plugins:
                mod = importlib.import_module("plugins." + plugin, ".")
                self.logger.info("Importing plugin.{}...".format(plugin))
                class_ = getattr(mod, "BotPlugin")
                self.plugins.append(class_(os.getcwd() + "/plugins/{}/".format(plugin), bot))
                self.modules.append(mod)
                self.logger.info("Successfully instantiated plugin!")
        else:
            new_modules = []
            for module in self.modules:
                mod = importlib.reload(module)
                self.logger.info("Attempting to reload plugin module with name {}...".format(module.__name__.split(".")[1]))
                class_ = getattr(mod, "BotPlugin")
                self.plugins.append(class_(os.getcwd() + "/plugins/{}/".format(module.__name__.split(".")[1]), bot))
                new_modules.append(mod)
                self.logger.info("Successfully reloaded and instantiated plugin!")
            self.modules = new_modules
        
        self.imported = True

        for plugin in self.plugins:
            if not plugin.get_commands() == None:
                for command in plugin.get_commands():
                    self.commands[command] = plugin
                    self.logger.info("Mapped command ({}) to plugin {}".format(command, plugin.get_name()))
            if plugin.has_message_access():
                self.message_plugins.append(plugin)
                self.logger.info("Gave plugin {} message access".format(plugin.get_name()))
            self.is_enabled[plugin.get_name()] = True

    def dynamically_load(self, bot):
        """
        NYI.
        Dynamically imports, initializes, and loads an external Python file.
        Sets the Plugin to True within self.is_enabled

        ...

        Parameters
        ----------
        bot: Bot
            The main Bot object responsible for sending and receiving messages
        """
        pass

    def reload_plugins(self, bot):
        """
        Reloads all Plugins.
        Allows for dynamic updating of Plugins.

        ...

        Parameters
        ----------
        bot: Bot
            The main Bot object responsible for sending and receiving messages
        """

        self.logger.warning("Attempting to reload all accessible plugins...")
        self.load_plugins(bot)
        self.logger.warning("Reloading complete!")

    def process_plugin(self, bot, message):
        """
        Processes Plugin's based on their command strings.
        If a valid command string is received by the Bot and found as a key within self.commands that Plugin's on_command method is called.
        Returns the result if the plugin is found and enabled.
        Returns a message if the command string is invalid or the plugin is disabled.

        ...

        Parameters
        ----------
        bot: Bot
            The main Bot object responsible for sending and receiving messages

        message: Message
            Message object detailing command, message, and Telegram user info
        """



        try:
            self.lock.acquire()

            if self.is_enabled[self.commands[message.command.command].get_name()]:
                self.logger.info("Processing command ({}) for plugin ({})".format(message.command.command, self.commands[message.command.command].get_name()))
                response = self.commands[message.command.command].on_command(message.command)
            else:
                self.logger.warning("Unable to process command {} as it is disabled".format(message.command.command))
                response =  {"type": "message", "message": "That command is currently disabled or does not exist."}

            self.lock.release()

            if response["type"] == "message":
                bot.send_message(message.chat.id, response["message"])
            elif response["type"] == "photo":
                bot.send_photo(message.chat.id, response["caption"], response["file_name"])
        except KeyError:
            self.logger.warning("Unable to process command {} as it is invalid".format(message.command.command))
            bot.send_message(message.chat.id, "Invalid command!\n'" + message.command.command + "'")
            self.lock.release()
        except Exception as e:
            self.logger.exception("An unknown exception occurred...")
            bot.send_message(message.chat.id, "I'm afraid I can't do that.\n'"+str(e)+"'")
            self.lock.release()

    def process_message(self, bot, message):
        """
        Processes all Plugins whose has_message_access() method returned True.
        These Plugins receive every message sent to the bot.
        Responds replies from the plugins should the associated plugins be enabled.

        ...

        Parameters:
        bot: Bot
            The main Bot object responsible for sending and receiving messages

        message: Message
            Message object detailing command, message, and Telegram user info
        """

        self.lock.acquire()

        for plugin in self.message_plugins:
            if self.is_enabled[plugin.get_name()]:
                reply = plugin.on_message(message)

                if reply:
                    bot.send_message(message.chat.id, reply)

        self.lock.release()

    def enable_plugin(self, plugin_name):
        """
        Sets a plugin as 'enabled' (True) within is_enabled.
        Returns True if the Plugin is successfully enabled and calls that Plugin's enable() method.
        Returns False if the Plugin is already enabled or if the Plugin does not exist.

        ...

        Parameters
        ----------
        plugin_name: str
            The name of the Plugin
        """

        for plugin in self.plugins:
            if plugin.get_name() == plugin_name:
                if not self.is_enabled[plugin.get_name()]:
                    self.logger.info("Enabling plugin with name ({})".format(plugin.get_name()))
                    self.is_enabled[plugin_name] = True
                    plugin.enable()
                    return True
                self.logger.warning("Unable to enable plugin with name ({}), it is already enabled".format(plugin.get_name()))
                return False
        self.logger.warning("Unable to enable plugin with name ({}), it does not exist!".format(plugin_name))
        return False

    def disable_plugin(self, plugin_name):
        """
        Sets a plugin as 'disabled' (False) within is_enabled.
        Returns True if the Plugin is successfully disabled and calls that Plugin's disable() method.
        Returns False if the Plugin is already disabled or if the Plugin does not exist.

        ...

        Parameters
        ----------
        plugin_name: str
            The name of the Plugin
        """

        for plugin in self.plugins:
            if plugin.get_name() == plugin_name:
                if self.is_enabled[plugin.get_name()]:
                    self.logger.info("Disabnling plugin with name ({})".format(plugin.get_name()))
                    self.is_enabled[plugin_name] = False
                    plugin.disable()
                    return True
                self.logger.warning("Unable to disable plugin with name ({}), it is already disabled".format(plugin.get_name()))
                return False
        self.logger.warning("Unable to disable plugin with name ({}), it does not exist!".format(plugin_name))
        return False

    def list_commands(self):
        """
        Returns a string detailing all Plugins and their registered commands
        """

        response = "Available Plugins\n-----------------\n"

        for plugin in self.plugins:
            response += plugin.get_name() + " Commands:\n\t"
            
            if not plugin.get_commands() == None:
                for command in plugin.get_commands():
                    response += command + ", "
                response = response[:len(response)-2]
            response += "\n"
        return response

    def list_listeners(self):
        """
        Returns a string detailing all Plugins that are currently listening for messages
        """

        return "Listeners:\n"+str(self.message_plugins)

    def plugin_help(self, plugin_name):
        """
        Returns a string containing the help message from a Plugin's get_help method
        """

        for plugin in self.plugins:
            if plugin.get_name() == plugin_name:
                return plugin.get_help()
        return "That plugin does not exist!"

    def list_plugins(self):
        """
        Returns a str listing all plugins
        """

        response = "The following plugins are loaded:\n"

        for plugin in self.plugins:
            response += plugin.get_name() + "\n"
        return response


        
