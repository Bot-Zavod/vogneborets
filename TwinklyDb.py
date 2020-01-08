import psycopg2
from contextlib import closing
from psycopg2.extras import DictCursor
from psycopg2.sql import SQL 
from psycopg2 import sql
import json
from os import environ

def run_query(stmt):
    dbname, user, password, host, port = environ['db_name'], environ['db_user'], environ['db_password'], environ['db_host'], int(environ['db_port'])
    with closing(psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)) as conn:
        with conn.cursor() as cursor:
            cursor.execute(stmt)
            conn.commit()
            return cursor.fetchall()

def run_query_nofetch(stmt):
    dbname, user, password, host, port = connectDB()
    with closing(psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)) as conn:
        with conn.cursor() as cursor:
        	# ETO NE PRAVILNO NO poidet!
        	try:
	            cursor.execute(stmt)
	            conn.commit()  
	        except Exception as e:
	        	print(str(e))     

class User:

    column_names = ['chat_id', 'first_name', 'last_name', 'username', 'language','reg_date']

    def __init__(self, chat_id ,first_name,last_name, username, user_id = None):
        self.chat_id = chat_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.user_id = user_id

    def __repr__(self):
        return f'User: {self.username}, id: {self.user_id}, chat_id: {self.chat_id}'

    #Add new user to database

    @classmethod
    def addNewUser(cls, chat_id, first_name, last_name, username, language):

    	# ADD language table

        stmt = SQL('INSERT INTO "Users" ({}) VALUES ({}, current_date)').format(
            SQL(',').join(map(sql.Identifier, cls.column_names)),
            SQL(',').join(map(sql.Literal, [chat_id, first_name, last_name, username, language])),
        )
        run_query_nofetch(stmt)


    #Get user by chat ID, return User object list

    @classmethod
    def getUser(cls, chat_id):
        stmt = SQL('SELECT * FROM "Users" WHERE chat_id = {}').format(
            SQL(',').join(map(sql.Literal, [chat_id])),
        )
        return [User(*el[1:], user_id = el[0]) for el in run_query(stmt)]

    @classmethod
    def setUserLang(cls, chat_id, lang):
        stmt = SQL('UPDATE "Users" SET language = {} WHERE chat_id = {}').format(
            sql.Literal(lang),sql.Literal(chat_id),
        )
        run_query_nofetch(stmt)

    @classmethod
    def getUserLang(cls, chat_id):
        stmt = SQL('SELECT language FROM "Users" WHERE chat_id = {}').format(
            sql.Literal(chat_id),
        )
        try:
            result = run_query(stmt)[0][0]
            return result
        except Exception as e:
            return 'en'
class Review:

    column_names = ['chat_id', 'q_json', 'form_id', 'lat', 'lon', 'adr', 'place', 'comment', 'mark']
    
    def __init__(self, user_id, q_json, form_id, lat, lon, adr, place, comment, mark, review_id = None):
        self.chat_id = chat_id
        self.q_json = q_json
        self.form_id = form_id
        self.lat = lat
        self.lon = lon
        self.adr = adr
        self.place = place
        self.comment = comment
        self.mark = mark
        self.review_id = review_id

    def __repr__(self):
        return f'Review: {self.q_json}, by: {self.chat_id}, place: {self.place}, comment: {self.comment}, id: {self.review_id}'

    @classmethod
    def getReview(cls, review_id):
        stmt = SQL('SELECT * FROM "Reviews" WHERE review_id = {}').format(
            SQL(',').join(map(sql.Literal, [review_id])),
        )
        return [Review(*el[1:], review_id = el[0]) for el in run_query(stmt)]

    @classmethod
    def addReview(cls, *args, **kwargs):
        stmt = SQL('INSERT INTO "Reviews" ({}, submit_time) VALUES ({}, current_timestamp)').format(
            SQL(',').join(map(sql.Identifier, cls.column_names)),
            SQL(',').join(map(sql.Literal, args)),
        )
        run_query_nofetch(stmt)

    @classmethod
    def getMark(cls, id):
        stmt = SQL('SELECT AVG(mark) FROM "Reviews" WHERE adr = {}').format(sql.Literal(id))
        result = run_query(stmt)
        if len(result) == 0:
        	return 0
        return(int(result[0][0]))

    @classmethod
    def getComments(cls, place_id,chat_id):
            stmt = SQL('SELECT comment FROM "Reviews" WHERE adr = {} and chat_id != {} ORDER BY submit_time DESC LIMIT 3;').format(sql.Literal(place_id), sql.Literal(chat_id))
            result = run_query(stmt)
            if len(result) == 0:
                return []
            return([msg[0] for msg in result])
    

#EXAMPLES

# User.addNewUser(100500, 'Testname', 'TestLastName','chat','unmae')
# print(User.getUser(100500)[0].checkLocation())
# print(User.getUser(100500)[0].updateLocation(100, 500))
# print(User.getUser(100500))
# print(Form.getForm(1))
# print(Form.addForm('TestYForm', [1,2]))
# print(Question.getQuestion(1, 'RU'))
# print(Question.getQuestion(1, 'UA'))
# print(Question.addQuestion('Hellot there?'))
# print(Review.getReview(1))
# print (type(Review.getReview(1)[0].q_json))
# Review.addReview(100500, json.dumps({'1':0}), 1,1,1,'Tereshkovoy10', 'ONPU', 'cmnt', 10)

# Form example
# print(Question.getQuestions([1,2,3], 'UA'))
# form = Form.getForm(1)[0]
# questions = Question.getQuestions(form.questions, 'UA')
# for q in questions:
#     print (q)
# print(Review.getMark('--'))
# print(Review.getComments('--', 100500))
# print(Review.isReviewEstimate('ChIJg8PGGlzUhg4RDMUagWtgV6E', 516233921))
# User.setUserLang(384341805, 'ru')
# print(User.getUserLang(384341805))