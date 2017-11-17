import random
from plugin import Plugin
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

def load(data_dir, bot):
	return Doge(data_dir, bot)

class Doge(Plugin):
	def __init__(self, data_directory, bot):
		self.dir = data_directory
		self.bot = bot
		self.parts = ["many", "very", "such", "much", "so", "wow"]
		self.words = []
		self.colors = []
		self.coords = []

		self.colors.append((52, 255, 0))  # Green
		self.colors.append((255, 0, 0))  # Red
		self.colors.append((0, 0, 255))  # Blue
		self.colors.append((255, 255, 0))  # Yellow
		self.colors.append((255, 128, 0))  # Orange
		self.colors.append((200, 0, 255))  # Purple

		self.coords.append((70, 100))
		self.coords.append((750, 200))
		self.coords.append((650, 460))
		self.coords.append((785, 700))
		self.coords.append((150, 600))

	def doge_it_up(self, words):
		try:
			image = Image.open(self.dir + "/doge_template.jpg")
			draw = ImageDraw.Draw(image)

			font = ImageFont.truetype("comic.ttf", 64)

			random.shuffle(self.colors)

			for word, color, coord in zip(words, self.colors, self.coords):
				print(word)
				draw.text(coord, word, color, font)

			image.save(self.dir + "\doge.jpg")

		except FileNotFoundError:
			return "Unable to find file {}/doge_template.jpg".format(self.dir)

	def on_command(self, command):
		if command.command == "doge":
			caption = ""
			top_words = sorted(self.words, key=len, reverse=True)[:5]
			random.shuffle(top_words)
			words_to_draw = []

			for word in top_words:
				choice = random.choice(self.parts)
				text = ""
				if choice == "wow":
					caption += choice
					text += choice
				else:
					caption += choice + " "+ word
					text += choice + " "+ word
				caption += "\n"
				words_to_draw.append(text)

			self.doge_it_up(words_to_draw)
			self.words = []
			return  {"type": "photo", "caption": caption.strip(),
					"file_name": self.dir+"/doge.jpg"}

	def get_commands(self):
		return {"doge"}

	def get_name(self):
		return "Doge"

	def get_help(self):
		return "Sends doge pictures!"

	def has_message_access(self):
		return True

	def on_message(self, message):
		self.words.extend(message.text.split(" "))
		return ""
