import random
import os
import re
import pickle

from plugin import Plugin


def load(data_dir, bot):
    return RPG_Plugin(data_dir, bot)


"""
Class for handling dice rolls
"""
class Roll():
    def __init__(self, init_string):
        init_string = init_string.lower()
        parts = init_string.split("d")

        if parts[0]:
            self.num = max(int(parts[0]), 1)  # How many dice to roll
        else:
            self.num = 1

        if parts[1]:
            self.size = int(parts[1])  # The size of the dice (i.e. d20)

            if self.size < 1:
                self.size = 1  # The size of the dice must be greater than 1
        else:
            self.size = 1

        self.rolls = []  # A list containing all rolls made
        self.roll()  # Rolls self.num dice of dice size self.size and stores them in self.rolls

    def roll(self):
        if self.rolls:
            return self.rolls
        for i in range(self.num):
            self.rolls.append(random.randint(1, self.size))
        return self.rolls

    def sum(self):
        return sum(self.rolls)


"""
Holds information on a player character utilizing dictionaries for stats and inventory
"""
class Character:
    def __init__(self, creator, name):
        self.creator = creator  # Establishes who is able to play as this character
        self.name = name
        self.inventory = {}
        self.stats = {}
        self.abilities = {}

    # Adds an item to this characters inventory
    def give_item(self, item, amount, desc):
        if item in self.inventory:
            self.inventory[item] = [desc, self.inventory[item][1] + amount]
        else:
            self.inventory[item] = [desc, amount]

    # Sets a stat to this characters inventory
    def set_stat(self, stat, num):
        self.stats[stat] = num

    def give_ability(self, ability, desc):
        self.abilities[ability] = desc

    # Returns an organized string of all stats held by this character
    def stat_string(self):
        result = self.name + ":"
        for stat in self.stats.keys():
            result += "\n" + stat + ": " + str(self.stats[stat])
        return result

    # Returns an organized string of all abilities held by this character
    def ability_string(self):
        result = self.name + ":"
        for abil in self.abilities.keys():
            result += "\n" + abil + ": " + str(self.abilities[abil])
        return result

    # Returns an organized string of all items held by this character
    def inventory_string(self):
        result = self.name + ":"
        for item in self.inventory.keys():
            result += "\n" + item + " (x" + str(self.inventory[item][1]) + ") - " + self.inventory[item][0]
        return result

    def remove_item(self, item_name):
        if item_name in self.inventory.keys():
            del self.inventory[item_name]
            return True
        return False

    def consume_item(self, item_name):
        if item_name in self.inventory.keys():
            if self.inventory[item_name][1] > 1:
                self.inventory[item_name][1] -= 1
                return True
            elif self.inventory[item_name][1] == 1:
                del self.inventory[item_name]
                return True
            return False
        return False

    def remove_stat(self, stat_name):
        if stat_name in self.stats.keys():
            del self.stats[stat_name]
            return True
        return False

    def remove_ability(self, ability_name):
        if ability_name in self.abilities.keys():
            del self.abilities[ability_name]
            return True
        return False


"""
Manages all created characters and loads characters for specific users
"""
class CharacterManager:
    def __init__(self, char_directory):
        self.dir = char_directory
        self.characters = {}
        self.load_char()

    def add_character(self, char_name, char):
        self.characters[char_name] = char

    def has_character(self, user, char_name):
        if char_name in self.characters.keys():
            char = self.characters[char_name]
            return char.creator == user
        return False

    def char_exists(self, char_name):
        return char_name in self.characters.keys()

    def get_character(self, char):
        return self.characters[char]

    def get_users(self):
        return list(self.characters.keys())

    def remove_char(self, user, char_name):
        if char_name in self.characters.keys():
            char = self.characters[char_name]

            if char.creator == user:
                del self.characters[char_name]
                return "RPGTools: Successfully deleted character " + char_name
            return "RPGTools: Unable to delete a character you did not create."
        return "RPGTools: That character does not exist!"

    # Saves self.characters dict to characters.file using pickle
    def save_char(self):
        with open(self.dir + "/characters.file", "wb") as f:
            pickle.dump(self.characters, f)
            f.seek(0)
            f.close()

    # Attempts to load self.characters dict from characters.file using pickle
    def load_char(self):
        try:
            if os.path.getsize(self.dir + "/characters.file") > 0:
                with open(self.dir + "/characters.file", "rb") as f:
                    self.characters = pickle.load(f)
                    f.seek(0)
                    f.close()
            print("RPGTools: Character file successfully loaded!")
        except FileNotFoundError:
            if not os.path.exists(self.dir):
                os.makedirs(self.dir)

            # Ensures that the character file is created.
            with open(self.dir + "/characters.file", "w+") as f:
                f.write("")
                f.seek(0)
                f.close()
            print("RPGTools: No character file exists, creating a new one.")


"""
Main Plugin class that manages command usage
"""
class RPG_Plugin(Plugin):
    def __init__(self, data_dir, bot):
        self.dir = data_dir
        self.manager = CharacterManager(self.dir)
        self.dm = ["Klawk"]

    def on_command(self, command):
        if command.command == "r" or command.command == "roll":
            return {"type": "message", "message": self.roll_dice(command)}
        elif command.command == "create_character":
            return {"type": "message", "message": self.create_character(command)}
        elif command.command == "show_stats":
            return {"type": "message", "message": self.show_stats(command)}
        elif command.command == "show_inventory":
            return {"type": "message", "message": self.show_inventory(command)}
        elif command.command == "show_abilities":
            return {"type": "message", "message": self.show_abilities(command)}
        elif command.command == "set_stat":
            return {"type": "message", "message": self.set_stat(command)}
        elif command.command == "give_item":
            return {"type": "message", "message": self.give_item(command)}
        elif command.command == "give_ability":
            return {"type": "message", "message": self.give_ability(command)}
        elif command.command == "rm_stat":
            return {"type": "message", "message": self.rm_stat(command)}
        elif command.command == "rm_item":
            return {"type": "message", "message": self.rm_item(command)}
        elif command.command == "rm_ability":
            return {"type": "message", "message": self.rm_ability(command)}
        elif command.command == "rm_char":
            return {"type": "message", "message": self.rm_char(command)}
        elif command.command == "chars":
            return {"type": "message", "message": self.chars()}
        elif command.command == "consume":
            return {"type": "message", "message": self.consume_item(command)}
        elif command.command == "set_dm":
            return {"type": "message", "message": self.set_dm(command)}
        elif command.command == "rm_dm":
            return {"type": "message", "message": self.rm_dm(command)}

    def get_commands(self):
        return {"r", "roll", "create_character", "show_stats", "show_inventory", "show_abilities", "set_stat",
                "give_item", "give_ability", "rm_stat", "rm_item", "rm_ability", "rm_char", "chars", "consume", "set_dm", "rm_dm"}

    def get_name(self):
        return "RPG Tools"

    def get_help(self):
        return "/roll <dice_expression>\n" \
               "/create_character <name>\n" \
               "/show_stats <char>\n" \
               "/show_inventory <char>\n" \
               "/show_abilities <char>\n" \
               "/set_stat <char>,<stat>,<amount>\n" \
               "/give_item <char>,<item>,<description>,<quantity>\n" \
               "/give_ability <char>,<ability>,<description>\n" \
               "/rm_stat <char>,<stat>\n" \
               "/rm_item <char>,<item>\n" \
               "/rm_ability <char>,<ability>\n" \
               "/rm_char <char>\n" \
               "/chars\n" \
               "/consume <char>,<item>\n" \
               "/set_dm <user>\n" \
               "/rm_dm <user>\n" \

    def on_message(self, message):
        pass
    
    def has_message_access(self):
        return False

    def enable(self):
        pass

    def disable(self):
        pass

    def roll_dice(self, command):
        user = command.mention if command.mention else command.user.username
        rolls = []
        constant = []
        mods = []
        parts = command.args.split("+")
        for part in parts:
            if "-" in part:
                try:
                    index = part.index("-", 1)
                    new_part = part[index:]
                    part = part[:index]
                    parts.append(new_part)
                except:
                    pass  # part is just a plain negative number
            part = part.strip()
            if re.search("\d+[dD]\d+", part):
                rolls.append(Roll(part))
            elif part.replace("-", "", 1).isdigit():
                constant.append(int(part))
            else:
                char_name = command.args.split("|")
                if self.manager.has_character(user, char_name[1]) and part in\
                        self.manager.get_character(char_name[1]).stats:
                    mods.append(part)
        result = user + " rolled:"
        total = 0
        for roll in rolls:
            total += roll.sum()
            result += "\n(" + ", ".join(str(s) for s in roll.rolls) + ") = " + str(roll.sum())
        for mod in mods:
            mod_value = int((self.manager.get_character(user).stats[mod] - 10) / 2)
            total += mod_value
            result += "\n + " + mod + " (" + str(mod_value) + ")"
        for c in constant:
            total += c
            result += "\n + " + str(c)
        result += "\n = " + str(total)
        return result

    def show_stats(self, command):
        user = command.user.username
        char = command.args

        if self.manager.has_character(user, char) or user in self.dm:
            return self.manager.get_character(char).stat_string()
        return user + " did not create that character!"

    def show_inventory(self, command):
        user = command.user.username
        char = command.args

        if self.manager.has_character(user, char) or user in self.dm:
            return self.manager.get_character(char).inventory_string()
        return user + " did not create that character!"

    def show_abilities(self, command):
        user = command.user.username
        char = command.args

        if self.manager.has_character(user, char) or user in self.dm:
            return self.manager.get_character(char).ability_string()
        return user + " did not create that character!"

    def set_stat(self, command):
        user = command.user.username
        parts = command.args.split(",")

        if len(parts) == 3:
            char = parts[0]

            if self.manager.has_character(user, char) or user in self.dm:
                self.manager.get_character(char).set_stat(parts[1].strip(), int(parts[2].strip()))
                self.manager.save_char()
                return self.manager.get_character(char).stat_string()
            return user + " did not create that character!"
        else:
            return "Invalid argument syntax! /set_stat <char>|<stat>|<amount>"

    def give_item(self, command):
        user = command.user.username
        parts = command.args.split(",")

        if len(parts) == 4:
            char = parts[0]

            # Format /give_item <char>|<name>|<description>|<quantity>
            if self.manager.has_character(user, char) or user in self.dm:
                item = parts[1].strip()
                desc = parts[2].strip()
                amount = int(parts[3].strip())

                self.manager.get_character(char).give_item(item, amount, desc)
                self.manager.save_char()
                return self.manager.get_character(char).inventory_string()
            return user + " did not create that character!"
        else:
            return "Invalid argument syntax! /give_item <char>|<item>|<description>|<quantity>"

    def give_ability(self, command):
        user = command.user.username
        parts = command.args.split(",")

        if len(parts) == 3:
            char = parts[0]

            # Format /give_ability <char>|<name>|<description>
            if self.manager.has_character(user, char) or user in self.dm:
                name = parts[1].strip()
                desc = parts[2].strip()

                self.manager.get_character(char).give_ability(name, desc)
                self.manager.save_char()
                return self.manager.get_character(char).ability_string()
            return user + " did not create that character!"
        else:
            return "Invalid argument syntax! /give_ability <char>|<ability>|<description>"

    def rm_stat(self, command):
        user = command.user.username
        parts = command.args.split(",")

        if len(parts) == 2:
            char = parts[0]

            if self.manager.has_character(user, char) or user in self.dm:
                self.manager.get_character(char).remove_stat(parts[1])
                self.manager.save_char()
                return self.manager.get_character(char).stat_string()
            return user + " did not create that character!"
        else:
            return "Invalid argument syntax! /rm_stat <char>|<stat>"

    def rm_item(self, command):
        user = command.user.username
        parts = command.args.split(",")

        if len(parts) == 2:
            char = parts[0]

            if self.manager.has_character(user, char) or user in self.dm:
                self.manager.get_character(char).remove_item(parts[1])
                self.manager.save_char()
                return self.manager.get_character(char).inventory_string()
            return user + " did not create that character!"
        else:
            return "Invalid argument syntax! /rm_item <char>|<item>"

    def rm_ability(self, command):
        user = command.user.username
        parts = command.args.split(",")

        if len(parts) == 2:
            char = parts[0]

            if self.manager.has_character(user, char) or user in self.dm:
                self.manager.get_character(char).remove_ability(parts[1])
                self.manager.save_char()
                return self.manager.get_character(char).ability_string()
            return user + " did not create that character!"
        else:
            return "Invalid argument syntax! /rm_ability <char>|<ability>"

    def rm_char(self, command):
        user = command.user.username
        char = command.args

        if self.manager.has_character(user, char):
            self.manager.remove_char(user, char)
            self.manager.save_char()
            return "Successfully deleted that character"
        return user + " did not create that character!"

    def chars(self):
        response = "The following characters exist:"

        for char in self.manager.get_users():
            response += "\n" + char

        return response

    def create_character(self, command):
        creator = command.user.username
        if self.manager.char_exists(command.args):
            return "That character already exists!"
        if command.args:
            self.manager.add_character(command.args, Character(creator, command.args))
            self.manager.save_char()
            return "Created character '" + command.args + "'' for player " + command.user.first_name
        else:
            return "Invalid argument syntax! /create_character <name>"

    def consume_item(self, command):
        user = command.user.username
        parts = command.args.split(",")

        if len(parts) == 2:
            char = parts[0]

            if self.manager.has_character(user, char) or user in self.dm:
                self.manager.get_character(char).consume_item(parts[1])
                self.manager.save_char()
                return self.manager.get_character(char).inventory_string()
            return user + " did not create that character!"
        else:
            return "Invalid argument syntax! /rm_item <char>|<item>"

    def set_dm(self, command):
        user = command.user.username
        new_dm = command.args

        if user in self.dm:
            if not new_dm in self.dm:
                self.dm.append(new_dm)
                return "Added {} to DM list".format(new_dm)
            return "{} is already on the DM list".format(new_dm)
        return "Sorry, you must already be a DM to use this command..."

    def rm_dm(self, command):
        user = command.user.username
        bad_dm = command.args

        if user in self.dm:
            if bad_dm in self.dm:
                self.dm.remove(bad_dm)
                return "Removed {} from DM list".format(bad_dm)
            return "{} is not on the DM list".format(bad_dm)
        return "Sorry, you must already be a DM to use this command..."
