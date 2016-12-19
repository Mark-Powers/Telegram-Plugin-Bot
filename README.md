# Telegram-Response-Bot
A simple chat-bot-like program, but with the ability for users to add custom responses. Created with the intention to 'moderate' a group chat in a way, by responding to frequently used phrases.

### Usage ###
- */newtrigger* - Adds a phrase that triggers a bot response. Requires phrase on first line, and subsequent lines contain responses to be chosen randomly.
- */list* - Lists all triggers

### Setup ###
Requirements
- [Python 3](https://www.python.org/)
  - [Requests](http://docs.python-requests.org/en/master/) module
- Telegram Bot Token
  - Make sure to change the privacy settings to see all messages
  - Write to a file named *token* in root directory of project, containing text **token="\<token here>"**
  
Run *bot.by* using Python 3. If running from a directory that isn't the project's root, you might need to change the **bot_dir** variable to be the path to the root.

### Structure ###
Inside the *triggers/* directory will be the triggers generated for the bot. For each trigger there is a text file, where the first line is phrase to respond to and subsequent lines are random responses. This is the same pattern as given to the */newtrigger* command. 

The *last_update* file generated stores the last message that has been processed.
