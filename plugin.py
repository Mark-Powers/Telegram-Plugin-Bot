class Plugin:
    def __init__(self, data_dir):
        pass

    def on_command(self, command):
        return "This plugin has no commands!"

    def get_commands(self):
        return {}

    def get_name(self):
        return "Base Plugin"

    def get_help(self):
        return "This plugin has no commands"
