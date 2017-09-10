import re
import os

class Config:
	def __init__(self, file_path):
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
				self.bot_username = re.search("bot_username=\"(.+)\"", config).group(1)
			except:
				self.bot_username = ""

			try:
				self.sleep_interval = int(re.search("sleep_interval=\"(.+)\"", config).group(1))
			except:
				self.sleep_interval = 2

			try:
				self.plugins = []
				p = re.search("plugins=\[(.+)\]", config).group(1).split(",")
				for plugin in p:
					self.plugins.append(plugin.strip())
			except:
				self.plugins = {}
