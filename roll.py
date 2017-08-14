import random

class Roll:
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