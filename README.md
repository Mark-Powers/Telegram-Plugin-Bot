# Telegram-Response-Bot
A [telegram](https://telegram.org/) bot, that helps role-playing, both live and in the messenger. In addition, there are a few 'moderation' features to this bot.

### Command Usage ###
#### General Commands ####
- */listtrigger* - Lists all triggers that the bot knows
- */newtrigger* - Adds a phrase that triggers a bot response. Requires trigger phrase on first line, and subsequent lines to contain responses to be chosen randomly
- */pasta* - Sends a random pasta message, or one specified by a keyword in the text after the command (see */listpasta*)
- */listpasta* - Lista all pasta keywords that the bot know
- */newpasta* - Adds a pasta. Requires pasta keyword(s) after command and remaining text starting on next line
#### Role-Play Commands ###
- */roll* - Rolls dice specified by an equation string. Items can be seperated by "+". Items can be given in dice notation (i.e. 3d6 rolls 3 6 sided die), as numerical values, or as a stat modifier (see */show_stats*, */set_stat*). Numerical values can be prefixed by a "-".
- */r* - An alias for */roll*.
- */create_character* - Creates a character with the name given after the command.
- */show_stats* - Shows the stats for the current user's character, or the user who's specified with @username after the command.
- */set_stat* - Sets the stat given after the command to the value specified next for the current user's character or for the username specified directly in the arguments. These stats can be used as modifiers in rolls too; a modifier of a stat *x* is *floor((x-10)/2)*. So doing */set_stat wis 12*, then doing */roll 1d20+wis* will add the wisdom modifier (1) to the roll.
- */show_inventory* - Shows all items for the user's character or for the user specified by @username.
- */give_item* - Gives an item to the user or user specified by @username. The arguments are item name, amount, and item description, seperated by the "|" character. 

### Setup ###
Requirements
- [Python 3](https://www.python.org/)
  - [Requests](http://docs.python-requests.org/en/master/) module
- Telegram Bot Token
  - Make sure to change the privacy settings to see all messages
  - Create a configuration file named "config.txt" in the directory you are running the executable from. Options are written to it one per line as **option="value"**. Options are descibed below
    - *token* - REQUIRED, where given value is your bot API token.
    - *bot_username* - Your bot's username (without the @). This is optional, but strongly recommened.
    - *bot_dir* - The directory of where the *bot.py* file is. Again, optional but strongly recommened.
    - *sleep_interval* - How often in seconds the bot checks for messages
  
Run *bot.by* using Python 3.

### Structure ###
Inside the *triggers/* directory will be the triggers generated for the bot. For each trigger there is a text file, where the first line is phrase to respond to and subsequent lines are random responses. This is the same pattern as given to the */newtrigger* command. 

### TODO ###
- Allow for subtraction of dice notation items and stat items in roll formulas
