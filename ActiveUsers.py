import time 
from Database.TwinklyDb import *

class Users():
	def __init__(self):
		self.__user_list = []

	def allUsers(self):
		return self.__user_list

	# add new user
	def addUser(self, chat_id, first_name, last_name, username, language):
		User.addNewUser(chat_id, first_name=first_name, last_name=last_name, username=username, language=language)
		if self.getUser(chat_id) == False:
			self.__user_list.append({
				'chat_id': chat_id, 
				'name': first_name, 
				'status': False, 
				'language': User.getUserLang(chat_id),
				'PLACES_VARIANT':[], 
				'USER_PLACE':'',
				'ANSWERS':[], 
				'QUESTIONS':[], 
				'ACTIVE_QUESTION': 0,
				'COMMENT': '',
				'LAST_ACTIVE': time.time()
				})
		else:
			return False

	# To change language
	def change_language(self, chat_id, language):
		for x in self.__user_list:
			if x['chat_id'] == chat_id:
				# save language change
				x.update({'language': language})	
				User.setUserLang(chat_id, language)

	# Get users that offline more then 30min
	def getOldUsers(self):
		res = []
		for i, x in enumerate(self.__user_list):
			if time.time()-x['LAST_ACTIVE'] >= 1600:  
				res.append(x['chat_id'])
		return res

	# Update Last active time user
	def update_last_activity(self, chat_id):
		for x in self.__user_list:
			if x['chat_id'] == chat_id:
				x.update({'LAST_ACTIVE': time.time()})				

	def delete_user(self, chat_id):
		for i, x in enumerate(self.__user_list):
			if x['chat_id'] == chat_id:
				del self.__user_list[i]

	def getUser(self, chat_id):
		# return user by chat_id
		for x in self.__user_list:
			if x['chat_id'] == chat_id:
				return x
		# if User is absent
		return False

	# change user status
	def changeUserStatus(self, chat_id, status):
		for x in self.__user_list:
			if x['chat_id'] == chat_id:
				x.update({'status': status})

	# change place taht user submit
	def changeUserPlace(self, chat_id, USER_PLACE):
		for x in self.__user_list:
			if x['chat_id'] == chat_id:
				# print('change user place')
				x.update({'USER_PLACE': USER_PLACE, 'PLACES_VARIANT': []})

				# get questions from DB
				form = Form.getForm(x['USER_PLACE'][2])[0]
				questions = Question.getQuestions(form.questions, 'UA')
				QUESTIONS = [q.content for q in questions]

				x.update({'QUESTIONS': QUESTIONS})

				
				

	# change variant of place
	def changePlacesVariant(self, chat_id, PLACES_VARIANT):
		for x in self.__user_list:
			if x['chat_id'] == chat_id:
				x.update({'PLACES_VARIANT': PLACES_VARIANT})

	# add Asnwer
	def addAnswer(self, chat_id, answer):
		for x in self.__user_list:
			if x['chat_id'] == chat_id:
				x['ANSWERS'].append(answer)

	def uppActiveQuestion(self, chat_id):
		for x in self.__user_list:
			if x['chat_id'] == chat_id:
				if  x['ACTIVE_QUESTION']+1 == len(x['QUESTIONS']):
					x['ACTIVE_QUESTION'] = 'comment'
				else:
					x['ACTIVE_QUESTION'] += 1

	def addComment(self, chat_id, text):
		for x in self.__user_list:
			if x['chat_id'] == chat_id:
				x.update({'ACTIVE_QUESTION': '', 'COMMENT': text})
				# send answers and comment to DB
				answers = x['ANSWERS']
				location = x['USER_PLACE'][1] #lat lon
				typ = x['USER_PLACE'][2] #type of place
				place_id = x['USER_PLACE'][3] #place_id

				# send to DB
				questions = Form.getForm(typ)[0].questions
				comment = text
				ans = list(map(lambda x: 1 if x == 'yes' else 0 if x == 'idn' else 0 ,answers))
				Review.addReview(chat_id, json.dumps(dict(zip(questions, ans))), typ,location[0], location[1], place_id, 'Org', comment, 100*sum(ans)//len(ans) )


if __name__ == '__main__':

	users = Users()
	# add new user
	users.addUser(1, 'Alexey')
	users.addUser(2, 'Vlad')
	users.addUser(3, 'Andrew')

	# get new user
	print(users.getUser(1))

	# change user parameters
	users.changeUserStatus(1, True)	
	users.changeUserPlace(1, 'asdgsfh')
	users.changePlacesVariant(1, ['asdgsdg','adgasdg','asgasdgsdg'])

	users.addAnswer(1, 'yes')
	users.addAnswer(1, 'no')
	users.addAnswer(1, 'wtf')
	users.addAnswer(1, 'wtf')
	users.addComment(1, 'erherthsfdh herthr therther ther th')
	print(users.getUser(1))