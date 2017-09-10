import os

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

class CharacterManager:
	def __init__(self, char_directory):
		self.__char_directory = char_directory
		self.__characters = {}
		for file in os.listdir(char_directory):
			if file.endswith(".txt"):
				with open(char_directory+"/"+file, 'r') as f:
					lines = f.readlines()
					char = Character(lines.pop(0).strip())
					for line in lines:
						if line.startswith("inventory:"):
							line = line.replace("inventory:","",1).strip()
							for item in line.split(":"):
								if item:
									group = item.split(",")
									char.give_item(group[0], int(group[1]), group[2])
						elif "=" in line:
							parts = line.split("=")
							char.set_stat(parts[0], int(parts[1]))
					self.__characters[file[:-4]] = char

	def add_character(self, user, char):
		self.__characters[user] = char

	def has_character(self, user):
		return user in self.__characters

	def get_character(self, user):
		return self.__characters[user]

	def get_users(self):
		return list(self.__characters.keys())

	def save_char(self, user):
		self.__characters[user].write_to_file(self.__char_directory+"/"+user+".txt")
