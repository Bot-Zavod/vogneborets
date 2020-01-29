import psycopg2
from contextlib import closing
from psycopg2.extras import DictCursor
from psycopg2.sql import SQL 
from psycopg2 import sql
import credentials
import json
import datetime
from statistics import mean 

def run_query(stmt):
    with closing(psycopg2.connect(dbname=credentials.dbname, user=credentials.user, password=credentials.password, host=credentials.host, port=credentials.port)) as conn:
        with conn.cursor() as cursor:
            cursor.execute(stmt)
            conn.commit()
            return cursor.fetchall()

def run_query_nofetch(stmt):
    with closing(psycopg2.connect(dbname=credentials.dbname, user=credentials.user, password=credentials.password, host=credentials.host, port=credentials.port)) as conn:
        with conn.cursor() as cursor:
        	# ETO NE PRAVILNO NO POX
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

    # Checks location of a user, returns True/False

    def checkLocation(self):
        stmt = SQL('SELECT EXTRACT(EPOCH FROM (current_timestamp - loc_timestamp)/60) FROM "User_locations" WHERE user_id = {}').format(
            SQL(',').join(map(sql.Literal, [self.chat_id])),
        )
        response = run_query(stmt)
        return False if len(response) == 0 else response[0][0] < 15.0

    # Updates location of a user

    def updateLocation(self, lat, lon):
        stmt = SQL('''INSERT INTO "User_locations" (user_id, lat, lon, loc_timestamp) VALUES ({}, current_timestamp)
                      ON CONFLICT (user_id) DO UPDATE SET lat = {}, lon = {}, loc_timestamp = current_timestamp''').format(
            SQL(',').join(map(sql.Literal, [self.chat_id, lat, lon])), sql.Literal(lat), sql.Literal(lon),
        )
        run_query_nofetch(stmt)

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

    column_names = ['chat_id', 'q_json', 'form_id', 'lat', 'lon', 'adr', 'place', 'comment', 'mark', 'submit_time']
    
    def __init__(self, chat_id, q_json, form_id, lat, lon, adr, place, comment, mark, submit_time, review_id = None):
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
        self.submit_time = submit_time

    def __repr__(self):
        return f'Review: {self.q_json}, by: {self.chat_id}, place: {self.place}, comment: {self.comment}, id: {self.review_id}'

    @classmethod
    def getReview(cls, review_id):
        stmt = SQL('SELECT * FROM "Reviews" WHERE review_id = {}').format(
            SQL(',').join(map(sql.Literal, [review_id])),
        )
        return [Review(*el[1:], review_id = el[0]) for el in run_query(stmt)]

    @classmethod
    def getMarkers(cls):
        stmt = SQL('SELECT adr, lat, lon, place, mark, comment FROM "Reviews"')
        reviews = run_query(stmt)
        marks = {}
        for r in reviews:
            if (r[0], r[3]) in marks:
                marks[(r[0], r[3])].mark.append(r[4])
                marks[(r[0], r[3])].comments.append(r[5])
            else:
                marks[(r[0], r[3])] = Mark(r[1], r[2], r[3], [r[4]], [r[5]])
        for m in marks.keys():
            marks[m].mark = int(mean(marks[m].mark))
        #return [Review(*el[1:], review_id = el[0]) for el in run_query(stmt)]
        return marks


    @classmethod
    def getReviews(cls):
        stmt = SQL('SELECT * FROM "Reviews"')
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
        print(result)
        if len(result) == 0:
        	return 0
        return(int(result[0][0]))

    @classmethod
    def getComments(cls, place_id,chat_id):
        stmt = SQL('SELECT comment FROM "Reviews" WHERE adr = {} and chat_id != {} ORDER BY submit_time DESC LIMIT 3;').format(sql.Literal(place_id), sql.Literal(chat_id))
        result = run_query(stmt)
        if len(result) == 0:
        	return ([],cls.getMark(place_id))
        return([msg[0] for msg in result], cls.getMark(place_id))

    @classmethod
    def isReviewEstimate(cls, place_id, chat_id):
        stmt = SQL('SELECT COUNT(*) FROM "Reviews" WHERE adr = {} and chat_id = {} and current_date - submit_time::date < 7;').format(
            sql.Literal(place_id), sql.Literal(chat_id)
        )
        result = run_query(stmt)
        print(result)
        return True if len(result) == 0 or result[0][0] == 0 else False 
    
class Mark:
    def __init__(self, lat, lng,name, mark, comments):
        self.lat = lat
        self.lng = lng
        self.name = name
        self.mark = mark
        self.comments = comments

    def __repr__(self):
        return str((self.lat, self.lng, self.name, self.mark, self.comments))


#EXAMPLES

# User.addNewUser(100500, 'Testname', 'TestLastName','chat','unmae')
# print(User.getUser(123123)[0].checkLocation())
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
# for el in Review.getReviews():
#     try:
#         print(el.submit_time.strftime("%d-%m-%Y %H:%M"))
#     except Exception as e:
#         pass
#for r in Review.getMarkers().values():
#    print(r)