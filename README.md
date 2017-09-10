# Telegram-Response-Bot
A [telegram](https://telegram.org/) bot that supports plugins. This allows for
creating bots with all sorts of functions without having to deal with much boiler
plate code.

### Setup ###
Requirements
- [Python 3](https://www.python.org/)
  - [Requests](http://docs.python-requests.org/en/master/) module
- Telegram Bot Token
  - Make sure to change the privacy settings to see all messages
  - Create a configuration file named "config.txt" in the directory you are running the executable from. Options are written to it one per line as **option="value"**. Options are descibed below
    - *token* - REQUIRED, where given value is your bot API token.
    - *bot_username* - Your bot's username (without the @). This is optional, but strongly recommended.
    - *bot_dir* - The directory of where the *bot.py* file is. Again, optional but strongly recommended.
    - *sleep_interval* - How often in seconds the bot checks for messages.
    - *plugins* - Module (file) names from the `plugins` folder seperates with commands beginning and ending with braces, much like creating a list in python.

Run *bot.by* using Python 3.

### TODO ###
- Allow for subtraction of dice notation items and stat items in roll formulas
