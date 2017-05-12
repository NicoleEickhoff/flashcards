# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import random
import re
import glob

# from bs4 import BeautifulSoup # uncomment to use to use AutoFlash
# import urllib.request

card_text_example = '''###Question: The *** module supplies classes for manipulating dates and times in both simple
and complex ways. While date and time arithmetic is supported, the focus of the implementation is on efficient
attribute extraction for output formatting and manipulation. For related functionality, see also the *** and ***
modules.

Answer: datetime, time, calendar

Note: Module calendar: General calendar related functions. Module time: Time access and conversions.'''

"""Make sure your cards are in a text file based on teh deck_blank.txt template"""
card_regex = re.compile('\#\#\#Question:(.*?)Answer:(.*?)Note:([^\#]|\n)', flags=re.S)


class Deck:
	def __init__(self, deck_path):
		self.deck_path = deck_path
		self.deck_text = open(deck_path).read()
		self.cards = []
	
	def make_cards(self):
		crds_iter = card_regex.finditer(self.deck_text)
		for m in crds_iter:
			question, answer, note = m.group(1), m.group(2), m.group(3)
			crd = Card(question, answer, note)
			self.cards.append(crd)


class Card:
	def __init__(self, question, answer, note):
		self.question = question
		self.answer = answer
		self.note = note
		self.tries = 0
		self.wrong_answers = []
		self.time_spent = 0
		self.you_got_it = False


class Game:
	def __init__(self):
		self.deck_paths = glob.glob('deck*.txt')
		self.current_deck_path = None
		self.current_deck = None
	
	def choose_deck(self):
		print('Select your deck by typing its number:\n')
		print(*enumerate(self.deck_paths), sep='\n')
		deck_num = int(raw_input('\ndeck number:  '))
		self.current_deck_path = self.deck_paths[deck_num]
		print('You chose {}. That is a great choice, we are all rooting for you.\n'.format(self.current_deck_path))
		raw_input('hit ENTER to start! After starting, type "THIS IS BULLSHIT" to quit. Type SPACE ENTER to submit '
		          'answer.\n')
		self.current_deck = Deck(self.current_deck_path)
	
	def play(self):
		self.choose_deck()
		self.current_deck.make_cards()
		while [c for c in self.current_deck.cards if not c.you_got_it]:
			card = random.choice([c for c in self.current_deck.cards if not c.you_got_it])
			card.tries += 1
			question, answer, note = card.question, card.answer, card.note
			print('*'*20, '\n')
			user_answer = self.multi_line_entry(question)
			if user_answer.strip().upper() == 'THIS IS BULLSHIT':
				self.choose_deck()
				self.play()
			if user_answer.strip() == answer.strip():
				print('GREAT JOB!  THAT IS CORRECT!!!')
				card.you_got_it = True
			else:
				print('\nThat is wrong.\n')
				card.wrong_answers.append(user_answer)
				print('Here is the right answer:\n{}\n'.format(answer.strip()))
				self.multi_line_entry(question, review=True)
		print('You got em all! Take a break!')
	
	def multi_line_entry(self, question, review=False):
		response = []
		if review:
			entry = raw_input('Type the correct answer for practice and press space enter:\n')
		else:
			entry = raw_input('Question:\n' + question.strip() + '\n\n')
		while entry != " ":
			response.append(entry)
			entry = raw_input("...")
		response = '\n'.join(response)
		print('YOU ENTERED:\n', response)
		return response
	
	def make_new_deck(self, deck_name):
		pass


if __name__ == "__main__":
	# aflash = AutoFlash()
	Game().play()

