class Character:
	def __init__(self, name):
		self.name = name
		self.inventory = {}
		self.stats = {}

	def give_item(self, item, amount, desc):
		if item in self.inventory:
			self.inventory[item] = (desc, self.inventory[item][1]+amount)
		else:
			self.inventory[item] = (desc, amount)
	
	def set_stat(self, stat, num):
		self.stats[stat] = num

	def stat_string(self):
		result = self.name + ":"
		for stat in self.stats.keys():
			result += "\n" + stat + ": " + str(self.stats[stat])
		return result
	
	def inventory_string(self):
		result = self.name + ":"
		for item in self.inventory.keys():
			result += "\n" + item + " (x" + str(self.inventory[item][1]) + ") - " + self.inventory[item][0]
		return result

	def write_to_file(self, file_name):
		output = self.name
		for stat in self.stats.keys():
			output += "\n"+stat+"="+str(self.stats[stat])
		output += "\ninventory"
		for item in self.inventory.keys():
			output+= ":" + item+","+str(self.inventory[item][1])+","+self.inventory[item][0]

		with open(file_name, 'w') as f:
			f.write(output)
