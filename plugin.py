from abc import ABC, abstractmethod

class Plugin:
    """
    Base class from which all plugins must inherit from.
    Contains abstract methods that inheriting members must implement to perform plugin
    functionality

    ...

    Methods
    -------
    on_message(message)
        Called per message when this plugin has access

    on_command(command)
        Called when a command from this plugin is received by the bot

    get_commands()
        Returns a set of strings that represents all commands supported by this plugin

    get_name()
        Returns a string representing the name of this plugin

    get_help()
        Returns a string containing a help message on how to use this plugin

    has_message_access()
        Returns a boolean: return True if this plugin should receive every message sent to the bot.
        If enabled, the on_message(message) method will be called within this plugin with every receiving message
    """

    def __init__(self, data_dir, bot):
        pass

    @abstractmethod
    def on_message(self, message):
        """
        If the method has_message_access(self) has returned true, this method gets called every time the bot receives the message
        
        Returns a string that represents a response to the received message. Return "" for no response.

        Parameters
        ----------
        message: str
            A message a user has sent to the bot
        """

        return "This gets called per message when a plugin has access!"

    @abstractmethod
    def on_command(self, command):
        """
        Receives a command string and reponds to it based on the plugins logic.

        Returns a dictionary dictating the type of media to be send by the bot, and the contents of the media.
        Valid types include the following:
            {"type": "message", "message": "Some message string here"}
            {"type": "photo", "caption": "Photo caption here", "file_name": "filename here"}

        Parameters
        ----------
        command: Command
            A Command object containing information on the specific command string received, arguments, chat mentions, the chat channel, and the user.
        """

        return {"type": "message", "message": "This gets called a command from this plugin is sent!"}

    @abstractmethod
    def get_commands(self):
        """
        Returns a set of strings dictating all command strings this plugin should respond to.

        When a command string is received, this plugin's on_command method is called.
        """

        return {}

    @abstractmethod
    def get_name(self):
        """
        Returns a string containing the name of this plugin.
        """

        return "Base Plugin"

    @abstractmethod
    def get_help(self):
        """
        Returns a string containing a help message on how to operate this plugin.
        """

        return "This plugin does nothing!"

    @abstractmethod
    def has_message_access(self):
        """
        Returns a boolean dictating whether this plugin should have complete message access.
        
        If True, this bot will receieve every message received by the bot, with each message calling this plugins on_message(self, message) method
        """

        return False
