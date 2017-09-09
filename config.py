import re
import os

class Config:
	def __init__(self, file_path):
		with open(file_path, 'r') as f:
			config = f.read()
			try:
				self.__token = re.search("token=\"(.+)\"", config).group(1)
			except:
				raise Exception("Config token not formatted correctly!")

			try:
				self.__bot_dir = re.search("bot_dir=\"(.+)\"", config).group(1)
			except:
				self.__bot_dir = os.path.abspath('')

			try:
				self.__bot_username = re.search("bot_username=\"(.+)\"", config).group(1)
			except:
				self.__bot_username = ""

			try:
				self.__sleep_time = int(re.search("sleep_interval=\"(.+)\"", config).group(1))
			except:
				self.__sleep_time = 2

			try:
				self.__plugins = re.search("plugins=\[(.+)\]", config).group(1).split(",")
			except:
				self.__plugins = 2

	def get_bot_dir(self):
		return self.__bot_dir

	def get_bot_username(self):
		return self.__bot_username

	def get_token(self):
		return self.__token

	def get_sleep_interval(self):
		return self.__sleep_time

	def get_plugins(self):
		return self.__plugins
