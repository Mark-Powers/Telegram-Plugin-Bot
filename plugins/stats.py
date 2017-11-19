import os

import numpy as np
import matplotlib.pyplot as plt

from plugin import Plugin

def load(data_dir, bot):
	return Stats(data_dir, bot)

class Stats(Plugin):
	def __init__(self, data_directory, bot):
		self.dir = data_directory
		self.bot = bot
		if not os.path.exists(self.dir):
			os.makedirs(self.dir)

	def get_name(self):
		return "Stats"

	def get_help(self):
		return "Don't mind me, just listening to your messages..."

	def get_commands(self):
		return {"plot"}

	def on_command(self, command):
		if command.command == "plot":
			self.plot()
			return  {"type": "photo", "caption": "",
					"file_name": self.dir+"/output.jpg"}

	def has_message_access(self):
		return True

	def on_message(self, message):
		with open(self.dir+"/log.csv", 'a') as f:
			f.write(",".join((str(message.date), message.sent_from.username, str(len(message.text))))+"\n")

	def plot(self):
		data = np.genfromtxt(self.dir+"/log.csv", delimiter=',', names=['date', 'name', 'length'])
		fig = plt.figure()
		ax1 = fig.add_subplot(111)
		ax1.set_title("Activity")
		ax1.set_xlabel('Date')
		ax1.set_ylabel('length')
		ax1.plot(data['date'], data['length'], color='r', label='the data')
		fig.savefig(self.dir+"/output.jpg")
