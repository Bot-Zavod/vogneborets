class Users():
	def __init__(self):
		self.__user_list = []

	def allUsers(self):
		return self.__user_list

	# add new user
	def addUser(self, chat_id, name):
		if self.getUser(chat_id) == False:
			self.__user_list.append({'chat_id': chat_id, 'name': name, 'status': False, 'PLACES_VARIANT':[], 'USER_PLACE':'', 'ANSWERS':[]})
		else:
			return False

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
				x.update({'USER_PLACE': USER_PLACE})
				x.update({'PLACES_VARIANT': []})

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
	print(users.getUser(1))