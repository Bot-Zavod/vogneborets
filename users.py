import time
import functools
import threading
from time import sleep

class UserManager:

    def __init__(self):
        self.user_removal_time = 1800
        self.currentUsers = {}
        self.userthread = threading.Thread(target=self.__remove_old_users)
        self.userthread.start()

    def __remove_old_users(self):
        while True:
            sleep(self.user_removal_time)
            print('deleteCycle')
            print(self.currentUsers)
            users_to_delete = []
            for user in self.currentUsers.values():
                if time.time() - user.lastActivityTime > self.user_removal_time:
                    users_to_delete.append(user.chat_id)
            for id in users_to_delete:
                self.delete_user(id)
                print('deleting user')

    def delete_user(self, chat_id):
        if chat_id in self.currentUsers:
            del self.currentUsers[chat_id]
        else:
            print(f'[WARNING]DELETING UNEXISTING USER {chat_id}')

    def create_user(self, user):
        if user.chat_id not in self.currentUsers:
            self.currentUsers[user.chat_id] = user
        else:
            print('ADDING EXISTING USER')
    # Users stored in dictionary with keys as 
    # Structure {
    #   user_id: User-class object 
    # }
    # chat_id

class User:
    def __init__(self, chat_id, username):
        self.chat_id = chat_id
        self.place = {}
        self.username = username
        self.location = ()
        self.questions = ()
        self.answers = {}
        self.lastActivityTime = time.time()

    def __repr__(self):
        return f'User {self.username} with chat id: {self.chat_id}'

    def refresh_action(func):
        def wrapper_refresh_time(self, *args, **kwargs):
            self.update_time()
            value = func(self, *args, **kwargs)
            return value
        return wrapper_refresh_time

    def update_time(self):
        self.lastActivityTime = time.time()

    @refresh_action
    def addLocation(self, location):
        self.location = location

    @refresh_action
    def addQuestions(self, questions):
        self.questions = questions

    @refresh_action
    def selectPlace(self, place):
        self.place = place

    @refresh_action
    def addAnswer(self, question, answer):
        # if question not in self.questions:
        #     print(f'[WARNING]: question {question} not found in {self.questions}')
        self.answers[question] = answer
    

# if __name__ == "__main__":
#     user = User(100500)
#     user.addQuestions([1,2,3,4,5])
#     user.addAnswer(1, 0)
#     print(user.answers)