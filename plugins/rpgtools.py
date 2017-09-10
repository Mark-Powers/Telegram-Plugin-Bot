import random
import os
import re

from plugin import Plugin

def load(data_dir):
	return RPG_Plugin(data_dir)

class Roll():
	def __init__(self, init_string):
		init_string = init_string.lower()
		parts = init_string.split("d")
		if parts[0]:
			self.num = max(int(parts[0]), 1)
		else:
			self.num = 1
		self.size = int(parts[1])
		if(self.size < 1):
			self.size = 1
		self.rolls = []
		self.roll()

	def roll(self):
		if self.rolls:
			return self.rolls
		for i in range(self.num):
			self.rolls.append(random.randint(1, self.size))
		return self.rolls

	def sum(self):
		return sum(self.rolls)

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
		self.dir = char_directory
		self.characters = {}
		if not os.path.exists(self.dir):
			os.makedirs(self.dir)
		for file in os.listdir(self.dir):
			if file.endswith(".txt"):
				with open(self.dir+"/"+file, 'r') as f:
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
					self.characters[file[:-4]] = char

	def add_character(self, user, char):
		self.characters[user] = char

	def has_character(self, user):
		return user in self.characters

	def get_character(self, user):
		return self.characters[user]

	def get_users(self):
		return list(self.characters.keys())

	def save_char(self, user):
		self.characters[user].write_to_file(self.dir+"/"+user+".txt")

class RPG_Plugin(Plugin):
	def __init__(self, data_dir):
		self.dir = data_dir
		self.manager = CharacterManager(self.dir+"/characters")

	def on_command(self, command):
		if command.command == "r" or command.command == "roll":
			return self.roll_dice(command)
		elif command.command == "create_character":
			return self.create_character(command)
		elif command.command == "show_stats":
			return self.show_stats(command)
		elif command.command == "show_inventory":
			return self.show_inventory(command)
		elif command.command == "set_stat":
			return self.set_stat(command)
		elif command.command == "give_item":
			return self.give_item(command)

	def get_commands(self):
		return {"r", "roll", "create_character", "show_stats", "show_inventory", "set_stat", "give_item"}

	def get_name(self):
		return "Roll!"

	def get_help(self):
		return "/roll <dice_expression>"

	def roll_dice(self, command):
		user = command.mention if command.mention else command.user.username
		rolls = []
		constant = []
		mods = []
		parts = command.args.split("+")
		for part in parts:
			if "-" in part:
				try:
					index = part.index("-",1)
					new_part = part[index:]
					part = part[:index]
					parts.append(new_part)
				except:
					pass # part is just a plain negative number
			part = part.strip()
			if re.search("\d+[dD]\d+",part):
				rolls.append(Roll(part))
			elif part.replace("-","",1).isdigit():
				constant.append(int(part))
			else:
				if self.manager.has_character(user) and part in self.manager.get_character(user).stats:
					mods.append(part)
		result = user + " rolled:"
		total = 0
		for roll in rolls:
			total += roll.sum()
			result += "\n(" + ", ".join(str(s) for s in roll.rolls) + ") = " + str(roll.sum())
		for mod in mods:
			mod_value = int((self.manager.get_character(user).stats[mod]-10)/2)
			total += mod_value
			result += "\n + " + mod +" (" + str(mod_value) + ")"
		for c in constant:
			total += c
			result += "\n + " + str(c)
		result += "\n = " + str(total)
		return result

	def show_stats(self, command):
		user = command.user.username
		if command.mention:
			user = command.mention
		if self.manager.has_character(user):
			return self.manager.get_character(user).stat_string()
		else:
			return user + " does not have a character!"

	def show_inventory(self, command):
		user = command.user.username
		if command.mention:
			user = command.mention
		if self.manager.has_character(user):
			return self.manager.get_character(user).inventory_string()
		else:
			return user + " does not have a character!"

	def set_stat(self, command):
		user = command.user.username
		if command.mention:
			user = command.mention
		if self.manager.has_character(user):
			# TODO could stats be multiple words?
			parts = command.args.split(" ")
			if len(parts)==2:
				self.manager.get_character(user).set_stat(parts[0], int(parts[1]))
				self.manager.save_char(user)
				return self.show_stats(command)
			else:
				return "Invalid syntax arguments!"
		else:
			return user + " does not have a character!"

	def give_item(self, command):
		user = command.user.username
		if command.mention:
			user = command.mention
		if self.manager.has_character(user):
			if command.args:
				parts = command.args.split("|")
				item = parts[0].strip()
				amount = 1
				desc = "no description"
				if len(parts) > 1 and parts[1].strip().isdigit():
					amount = int(parts[1].strip())
				if len(parts) > 2:
					desc = parts[2].strip()
				self.manager.get_character(user).give_item(item, amount, desc)
				self.manager.save_char(user)
				return self.show_inventory(command)
			else:
				return "Requires at least one argument!"
		else:
			return user + " does not have a character!"

	def create_character(self, command):
		if command.args:
			self.manager.add_character(command.user.username, Character(command.args))
			self.manager.save_char(command.user.username)
			return "Created character '" + command.args + "'' for player " + command.user.first_name
		else:
			return "Name your character!"
