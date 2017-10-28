class Plugin:
    def __init__(self, data_dir, bot):
        pass

    def on_message(self, message):
        return "This gets called per message when a plugin has access!"

    def on_command(self, command):
        return "This gets called a command from this plugin is sent!"

    def get_commands(self):
        return {}

    def get_name(self):
        return "Base Plugin"

    def get_help(self):
        return "This plugin does nothing!"

    def has_message_access(self):
        return False
