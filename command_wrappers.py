class Command:
	"""
	Class containing information on the command receieved in a Telegram message.
	"""

	def __init__(self, message):
		"""
		Parameters
		----------
		message: Message
			Message object that contains property information on a Telegram message.

		Properties
		----------
		self.command: string
			Contains the command string received.

		self.mention: string
			Contains the nickname of another Telegram user embedded within the message.

		self.args: string
			string of all text following the command string.

		self.chat: string
			The chat id of the Telegram group from which the command string was sent from.

		self.user: string
			The nickname of the user who sent the command string.
		"""

		text = message.text[1:]
		args_index = text.index(" ") if " " in text else len(text)
		text = text[args_index+1:]
		user_match = re.search("@(\w+)", text)
		
		self.command = text[:args_index]
		self.mention = user_match.group(1) if user_match else ""
		self.args = text.strip()
		self.chat = message.chat
		self.user = message.sent_from


class User:
	"""
	Class containing information on the user who sent a message on Telegram
	"""

	def __init__(self, user):
		"""
		Parameters
		----------
		user: dictionary
			contains information on a Telegram user after they send a message seen by the bot
			includes the user id, their first name, and their username

		Properties
		----------
		self.id: string
			The user/chatroom id of a Telegram user

		self.first_name: string
			The first name of a Telegram user

		self.username: string
			The username a Telegram user has chosen (ex. @Nickname or Nickname)
		"""

		self.id = user["id"]
		self.first_name = user["first_name"]
		self.username = user["username"] if "username" in user else self.first_name


class Chat:
	"""
	Class that contains information on the chat id and type from a message sent by a Telegram user.
	"""

	def __init__(self, chat):
		"""
		Parameters
		----------
		chat: dictionary
			dictionary object that contains the chat id and the chat type.

		Properties
		----------
		self.id: string
			The Telegram chat/channel id from which a message was received.

		self.type: string
			The Telegram chat type (ex. channel, chatroom, etc.)
		"""

		self.id = chat["id"]
		self.type = chat["type"]


class Message:
	"""
	Object that contains properties of Telegram message info
	"""

	def __init__(self, message):
		"""
		Parameters
		----------
		message: dictionary
			dictionary object that contains message information sent by telegram.

		Properties
		----------
		self.date: string
			String Date at which the message was sent.

		self.sent_from: string
			String Telegram user that sent the message.
		
		self.chat: Chat obj
			String chat/channel id from which the message was received.

		self.text: string
			String containing the message sent.

		self.is_command: Boolean
			Boolean determining if this contains the command prefix (default="/").

		self.command: Command
			Command object containing extensive information on the message and command string.
			Sent to the plugin that manages the designated command string should it exist.
		"""

		self.date = message["date"]
		self.sent_from = User(message["from"])
		self.chat = Chat(message["chat"])
		self.text = message["text"].strip() if "text" in message else ""
		self.is_command = self.text.startswith("/")
        
		if self.is_command:
			self.command = Command(self)