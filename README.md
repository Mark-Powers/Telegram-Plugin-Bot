# Telegram-Plugin-Bot
A [telegram](https://telegram.org/) bot that supports plugins. This allows for
creating bots with all sorts of functions without having to deal with much boiler
plate code.

### Setup ###
Requirements
- [Python 3](https://www.python.org/)
  - [Requests](http://docs.python-requests.org/en/master/) module
- Telegram Bot Token
  - Make sure to change the privacy settings to see all messages

Run *start.py* using Python 3. The first time it is a ran, you will be prompted to enter your bot's token, directory for the bot, sleep interval, and a list of plugins to load. This will be saved in `config.txt`.
