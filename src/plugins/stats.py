import os

import numpy as np
import matplotlib.pyplot as plt

from plugin import Plugin

class BotPlugin(Plugin):
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

	def enable(self):
		pass

	def disable(self):
		pass

	def plot(self):
		data = np.genfromtxt(self.dir+"/log.csv", delimiter=',', names=['date', 'name', 'length'])
		chatMap = {}
		for x in data:
			date = np.int64(np.int64(x[0])/(60*60*24))
			if date in chatMap:
				#print("same date!")
				chatMap[date] += x[2]
			else:
				chatMap[date] = x[2]
		#print(chatMap)
		#[(np.int64(np.int64(x[0])/3), x[1], x[2]) for x in data]

		data = np.array(list(chatMap.items()), dtype=[('date', '<i8'), ('length', '<f8')])
		'''
		print(data['length'])
		print(len(data['length']))
		plt.bar(len(data['length']), data['length'], .5, color="blue")
		fig = plt.gcf()
		'''
		fig = plt.figure()
		ax1 = fig.add_subplot(111)
		ax1.set_title("Activity")
		ax1.set_xlabel('Date')
		ax1.set_ylabel('length')
		ax1.plot(data['date'], data['length'], 'ro-')
		#plt.plot([1,2,3,4], [1,4,9,16], 'ro')
		fig.savefig(self.dir+"/output.jpg")
