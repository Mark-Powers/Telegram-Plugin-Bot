import re
import os

class Config:
	"""
	Reads writes information to/from the program's configuration file.

	...

	Methods
	-------
	write_config(file_path)
		Attempts to write out configuration info to the Configuration file.
	"""

	def __init__(self, file_path=None):
		"""
		Attempts to initally read existing data within the configuation file.

		...

		Parameters
		---------
		file_path: str
			Designated path to the configuration file.
		"""

		if not file_path:
			return
		with open(file_path, 'r') as f:
			config = f.read()
			try:
				self.token = re.search("token=\"(.+)\"", config).group(1)
			except:
				raise Exception("Config token not formatted correctly!")

			try:
				self.bot_dir = re.search("bot_dir=\"(.+)\"", config).group(1)
			except:
				self.bot_dir = os.path.abspath('')

			try:
				self.sleep_interval = int(re.search("sleep_interval=\"(.+)\"", config).group(1))
			except:
				self.sleep_interval = 2

			try:
				self.threads = int(re.search("threads=\"(.+)\"", config).group(1))
			except:
				self.threads = 1

			try:
				self.plugins = []
				p = re.search("plugins=\[(.+)\]", config).group(1).split(",")
				for plugin in p:
					self.plugins.append(plugin.strip())
			except:
				self.plugins = {}

	def write_config(self, file_path):
		"""
		Attempts to write out configuration info to the Configuration file.

		...

		Parameters
		----------
		file_path: str
			Designated path to the configuration file.
		"""

		with open(file_path, 'w') as f:
			f.write("token=\""+self.token+"\"\n")
			f.write("bot_dir=\""+self.bot_dir+"\"\n")
			f.write("sleep_interval=\""+str(self.sleep_interval)+"\"\n")
			f.write("threads=\""+str(self.threads)+"\"\n")
			f.write("plugins=["+",".join(self.plugins)+"]\n")

class ConfigWizard:
	"""
	Initializes the configuration file with information inputted by the user.
	"""

	def __init__(self, file_path):
		"""
		Attempts to create the configuration file through user inputted data.
		Saves inputs to the configuration file.

		...

		Parameters
		----------
		file_path:str
			Designated path to the configuration file.
		"""

		self.conf = Config()
		print("No config.txt file found, making one instead!")
		self.conf.token = input("What is your bots token?\n")
		self.conf.bot_dir = input("What is the abs path of the directory with bot.py?\n")
		self.conf.sleep_interval = int(input("How many seconds should be between fetches of new messages?\n"))
		self.conf.threads = int (input("How many threads would you like to use? (Recommended 1)\n"))
		self.conf.plugins = input("What plugins would you like to use (seperate with ',')?\n").split(",")
		self.conf.write_config(file_path)
