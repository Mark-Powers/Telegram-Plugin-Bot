from abc import ABC, abstractmethod

class Plugin:

    def __init__(self, data_dir, bot):
        pass

    @abstractmethod
    def on_message(self, message):
        return "This gets called per message when a plugin has access!"

    @abstractmethod
    def on_command(self, command):
        return {"type": "message",
                "mesasge": "This gets called a command from this plugin is sent!"}

    @abstractmethod
    def get_commands(self):
        return {}

    @abstractmethod
    def get_name(self):
        return "Base Plugin"

    @abstractmethod
    def get_help(self):
        return "This plugin does nothing!"

    @abstractmethod
    def has_message_access(self):
        return False
