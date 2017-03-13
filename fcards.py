import random
import re
import glob


from bs4 import BeautifulSoup
import urllib.request

card_text_example = '''###Question: The *** module supplies classes for manipulating dates and times in both simple and complex ways. While date and time arithmetic is supported, the focus of the implementation is on efficient attribute extraction for output formatting and manipulation. For related functionality, see also the *** and *** modules.

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
		deck_num = int(input('\ndeck number:  '))
		self.current_deck_path = self.deck_paths[deck_num]
		print('You chose {}. That is a great choice, we are all rooting for you.\n'.format(self.current_deck_path))
		input('hit ENTER to start! After starting, type "THIS IS BULLSHIT" to quit\n')
		self.current_deck = Deck(self.current_deck_path)
	
	def play(self):
		self.current_deck.make_cards()
		while [c for c in self.current_deck.cards if not c.you_got_it]:
			card = random.choice([c for c in self.current_deck.cards if not c.you_got_it])
			card.tries += 1
			question, answer, note = card.question, card.answer, card.note
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
		print('You got em all! Take a break!')
				
	
	def multi_line_entry(self, question, review=False):
		response = []
		if review:
			entry = input('Type the correct answer for practice and press enter:\n')
		else:
			entry = input('Question:\n' + question.strip() + '\n\n')
		while entry != " ":
			response.append(entry)
			entry = input("...")
		response = '\n'.join(response)
		print('YOU ENTERED:\n', response)
		return response

class AutoFlash:
	def __init__(self):
		self.p3mods = self.get_modules()
		self.choose_module()
		self.make_mod_fcs()
		
	
	def get_modules(self):
		
		modules = 'https://docs.python.org/3/py-modindex.html'
		data = urllib.request.urlopen(modules)
		soup = BeautifulSoup(data, 'html.parser')
		a_tags = soup.find_all('a')
		modules = [a['href'] for a in a_tags if a['href'].startswith('library')]
		modules = list(enumerate([a.split('-')[-1] for a in modules]))
		return modules
	
	def choose_module(self):
		print('Select module number: ', *self.p3mods, sep='\n')
		mod_num = input('TYPE HERE: ...')
		self.active_mod = self.p3mods[int(mod_num)][1]
		
	def make_mod_fcs(self):
		mod_path = 'https://docs.python.org/3/library/{}.html'.format(self.active_mod)
		print(mod_path)
		mod_data = urllib.request.urlopen(mod_path)
		msoup = BeautifulSoup(mod_data, 'html.parser')
		self.dl_class_tags = msoup.find_all('dl', attrs={"class": "class"})
		self.dl_function_tags = msoup.find_all('dl', attrs={"class": "function"})
		self.dl_data_tags = msoup.find_all('dl', attrs={"class": "data"})
		self.function_fc_list = []
		self.data_fc_list = []
		self.method_fc_list = []
		self.class_fc_list = []
		self.make_class_and_method_fc(msoup)
		self.make_function_fc()
		self.make_data_fc()
		self.generate_deck()
	
	def make_class_and_method_fc(self, msoup):
		dl_class_tags = msoup.find_all('dl', attrs={"class": "class"})
		for ctag in dl_class_tags:
			tag_text = ctag.get_text()
			answer_question = tag_text.split('¶', maxsplit=1)
			self.class_fc_list.append([answer_question[1].strip(), answer_question[0].strip()])
			dl_method_tags = ctag.find_all('dl', attrs={"class": "method"})
			for mtag in dl_method_tags:
				mtag_text = mtag.get_text()
				manswer_question = mtag_text.split('¶', maxsplit=1)
				self.method_fc_list.append(
					['method of {0}: {1}'.format(answer_question[0].strip(), manswer_question[1].strip()),
					 manswer_question[0].strip()])
		if not self.method_fc_list:
			dl_method_tags = msoup.find_all('dl', attrs={"class": "method"})
			for mtag in dl_method_tags:
				mtag_text = mtag.get_text()
				manswer_question = mtag_text.split('¶', maxsplit=1)
				self.method_fc_list.append(['method: {0}'.format(manswer_question[1].strip()),
				                       manswer_question[0].strip()])
	
	def make_function_fc(self):
		for ftag in self.dl_function_tags:
			tag_text = ftag.get_text()
			# print('^^^^^^^^', tag_text)
			answer_question = tag_text.split('¶', maxsplit=1)
			try:
				self.function_fc_list.append([answer_question[1].strip(), answer_question[0].strip()])
			except IndexError as err:
				print(err)
	
	def make_data_fc(self):
		for dtag in self.dl_function_tags:
			tag_text = dtag.get_text()
			# print('^^^^^^^^', tag_text)
			answer_question = tag_text.split('¶', maxsplit=1)
			try:
				self.data_fc_list.append([answer_question[1].strip(), answer_question[0].strip()])
			except IndexError as err:
				print(err)
	
	def generate_deck(self):
		
		with open('deck_{0}.txt'.format(self.active_mod), 'a') as f:
			for fc_list in [self.class_fc_list, self.method_fc_list, self.function_fc_list, self.data_fc_list]:
				for n in range(len(fc_list)):
					q = fc_list[n][0].replace('\n', '  ')
					# print('###########q:', q)
					a = fc_list[n][1]
					# print('###########a:', a)
					entry = '###Question:{0}\n\nAnswer:{1}\n\nNote:\n\n'.format(q, a)
					f.write(entry)

	

aflash = AutoFlash()

# if user_answer.strip() == testcard[1].strip():
# 					print('\n\n' + 'CORRECT !!!' * 8 + '\n', '\n' + '*********' * 6 + '\n', testcard[-1],
# 					      '\n' + '*********' * 6 + '\n')
# 					flashes2.remove(flashes2[x])
# 					print(len(flashes2))
# 					print("#" * 30 + '\n')
# 				else:
# 					print('\n\n' + 'WRONG !!!' * 8 + '\nTHE CORRECT ANSWER IS: \n' + testcard[1].strip(),
# 					      '\n' + '*********' * 6 + '\n' + testcard[2].strip() + '\n')
# 					print("#" * 30 + '\n')
# 					user_answer = multi_line_entry(testcard)
# 					print("#" * 30 + '\n')
		
		


# game = game()
# game.choose_deck()
# game.play()


game = Game()


# text = open('deck_practice.txt').read()


# print(len([x for x in card_regex.findall(text)]), sep='\n')

# print(card_regex.findall(text))

# lines = text.split('\n')
#
# flashcards = []
# for line in lines:
#
# 	if '===' in line and 'LEARNED' not in line and '\t' not in line:
# 		answer_start = line.index('===')
# 		answer = line[answer_start:]
# 		question = line[:answer_start] + '{ '
# 		card = [question, answer]
# 		flashcards.append(card)
#
#
# def game(flashes):
# 	flashes2 = flashes
# 	for tries in range(50):
# 		if len(flashes2) > 0:
# 			print('you are on try', tries)
# 			for i in range(len(flashes2) - 1):
# 				testcard = random.choice(flashes2)
# 				x = flashes2.index(testcard)
# 				user_answer = input(testcard[1] + '\n Answer:')
# 				if user_answer == testcard[0][:-1]:
# 					print('correct')
# 					flashes2.remove(flashes2[x])
# 					print(len(flashes2))
# 				else:
# 					print('wrong', testcard[0][:-1])
#
#
# ##Game 2
#
# ##OS section to get list of decks
# cwd = os.getcwd()
# decks = [deck for deck in os.listdir(cwd) if 'longflash' in deck]
# promptString = "Choose deck: (number), 'longflash[x]\n"
# for i in range(len(decks)):
# 	promptString += "({0}, {1})\n".format(i, decks[i][9:])
#
# # decks = ['longflashpython.txt', 'longflashcss.txt', 'longflashcl.txt', 'longflashsass.txt', 'longflashjquery.txt']
# decknum = input(promptString)
# # decknum = input("Choose deck:"+str([(i, decks[i]) for i in range(len(decks))])+'\n')
#
# # decknum = raw_input("Choose deck: (0) %s (1) %s or (2) %s or (3) %s or (4) %s"%(decks[0], decks[1], decks[2],
# # decks[3], decks[4])+'\n')
# with open(decks[int(decknum)]) as f:
# 	text2 = f.read()
#
# subprocess.run("open {0}".format(decks[int(decknum)]), shell=True)
# # print text2
# text2 = text2.replace('\t###Question', '###LEARNED')
# lines2 = text2.split('###')
# lines2 = [i.replace('\n', '###') for i in lines2 if len(i) > 1]
# # print lines2
# flashcards2 = []
# for line in lines2:
# 	# print('this is the line:', line[:20])
# 	if 'LEARNED' not in line:
# 		answer_start = line.index('Answer:') + 7
# 		if "Note" in line:
# 			note_start = line.index('Note:')
# 			answer = line[answer_start:note_start]
# 			question = line[:answer_start]
# 			note = line[note_start:]
# 			card = [question.replace('###', '\n'), answer.replace('###', '\n'), note.replace('###', '\n')]
# 			if len(card[0]) > 19:
# 				flashcards2.append(card)
# 		else:
# 			answer = line[answer_start:]
# 			question = line[:answer_start]
# 			card = [question.replace('###', '\n'), answer.replace('###', '\n')]
# 			if len(card[0]) > 19:
# 				flashcards2.append(card)
# 			# print 'card[0]', card[0], len(card[0])
# 			# print 'flashcards2:', flashcards2
#
#
# def game2(flashes):
# 	flashes2 = flashes
# 	for tries in range(50):
# 		if len(flashes2) > 0:
# 			print('you are on round', tries)
# 			for i in range(len(flashes2)):
# 				testcard = random.choice(flashes2)
# 				# print 'testcard is', testcard
# 				x = flashes2.index(testcard)
# 				user_answer = multi_line_entry(testcard)
# 				if user_answer.strip() == testcard[1].strip():
# 					print('\n\n' + 'CORRECT !!!' * 8 + '\n', '\n' + '*********' * 6 + '\n', testcard[-1],
# 					      '\n' + '*********' * 6 + '\n')
# 					flashes2.remove(flashes2[x])
# 					print(len(flashes2))
# 					print("#" * 30 + '\n')
# 				else:
# 					print('\n\n' + 'WRONG !!!' * 8 + '\nTHE CORRECT ANSWER IS: \n' + testcard[1].strip(),
# 					      '\n' + '*********' * 6 + '\n' + testcard[2].strip() + '\n')
# 					print("#" * 30 + '\n')
# 					user_answer = multi_line_entry(testcard)
# 					print("#" * 30 + '\n')
#
#
# def multi_line_entry(testcard):
# 	response = []
# 	# entry = "answer"
# 	entry = input(testcard[0] + '\n')
# 	while entry != " ":
# 		response.append(entry)
# 		entry = input("...")
# 	# entry = "submit"
# 	response = '\n'.join(response)
# 	print(response)
# 	return response
#
#
# def which_game():
# 	game_name = 'multi'
# 	game_name = input("'single' or 'multi' line code\n")
# 	if game_name == 'single':
# 		game(flashcards)
# 	else:
# 		game2(flashcards2)


# which_game()
# game2(flashcards2)

