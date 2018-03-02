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
		self.colors = [(52, 255, 0), #Green
					   (255, 0, 0), #Red
					   (0, 0, 255), # Blue
					   (255, 255, 0), #Yellow
					   (255, 128, 0), #Orange
					   (200, 0, 255)] #Purple
		self.coords = [(70, 100), (750, 200), (650, 460), (785, 700),(150, 600)]

	def doge_it_up(self, words):
		try:
			image = Image.open(self.dir + "/doge.jpg")
			draw = ImageDraw.Draw(image)

			try:
				font = ImageFont.truetype("comic.ttf", 64)
			except:
				font = ImageFont.load_default()
			random.shuffle(self.colors)

			for word, color, coord in zip(words, self.colors, self.coords):
				print(word)
				draw.text(coord, word, color, font)

			image.save(self.dir + "/output.jpg")

		except FileNotFoundError:
			return "Unable to find file {}/doge.jpg".format(self.dir)

	def on_command(self, command):
		if command.command == "doge":
			top_words = sorted(self.words, key=len, reverse=True)[:5]
			random.shuffle(top_words)
			words_to_draw = []

			for word in top_words:
				choice = random.choice(self.parts)
				words_to_draw.append(choice if choice == "wow" else choice + " "+ word)

			self.doge_it_up(words_to_draw)
			self.words = []
			return  {"type": "photo", "caption": "",
					"file_name": self.dir+"/output.jpg"}

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
