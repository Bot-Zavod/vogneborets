import psycopg2
from contextlib import closing
from psycopg2.extras import DictCursor
from psycopg2.sql import SQL 
from psycopg2 import sql
import credentials
import json

def run_query(stmt):
    with closing(psycopg2.connect(dbname=credentials.dbname, user=credentials.user, password=credentials.password, host=credentials.host, port=credentials.port)) as conn:
        with conn.cursor() as cursor:
            cursor.execute(stmt)
            conn.commit()
            return cursor.fetchall()

def run_query_nofetch(stmt):
    with closing(psycopg2.connect(dbname=credentials.dbname, user=credentials.user, password=credentials.password, host=credentials.host, port=credentials.port)) as conn:
        with conn.cursor() as cursor:
            cursor.execute(stmt)
            conn.commit()        

class User:

    column_names = ['chat_id', 'first_name', 'last_name', 'username']

    def __init__(self, chat_id ,first_name,last_name, username, user_id = None):
        self.chat_id = chat_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.user_id = user_id

    def __repr__(self):
        return f'User: {self.username}, id: {self.user_id}, chat_id: {self.chat_id}'

    @classmethod
    def addNewUser(cls, chat_id, first_name, last_name, username):
        stmt = SQL('INSERT INTO "Users" ({}) VALUES ({})').format(
            SQL(',').join(map(sql.Identifier, cls.column_names)),
            SQL(',').join(map(sql.Literal, [chat_id, first_name, last_name, username])),
        )
        run_query_nofetch(stmt)

    @classmethod
    def getUser(cls, chat_id):
        stmt = SQL('SELECT * FROM "Users" WHERE chat_id = {}').format(
            SQL(',').join(map(sql.Literal, [chat_id])),
        )
        return [User(*el[1:], user_id = el[0]) for el in run_query(stmt)]

    def checkLocation(self):
        stmt = SQL('SELECT EXTRACT(EPOCH FROM (current_timestamp - loc_timestamp)/60) FROM "User_locations" WHERE user_id = {}').format(
            SQL(',').join(map(sql.Literal, [self.chat_id])),
        )
        return run_query(stmt)[0][0] < 15.0

    def updateLocation(self, lat, lon):
        stmt = SQL('''INSERT INTO "User_locations" (user_id, lat, lon, loc_timestamp) VALUES ({}, current_timestamp)
                      ON CONFLICT (user_id) DO UPDATE SET lat = {}, lon = {}, loc_timestamp = current_timestamp''').format(
            SQL(',').join(map(sql.Literal, [self.chat_id, lat, lon])), sql.Literal(lat), sql.Literal(lon),
        )
        run_query_nofetch(stmt)
        

class Form:

    column_names = ['name', 'questions']

    def __init__(self, name, questions, form_id = None):
        self.name = name
        self.questions = questions
        self.form_id = form_id

    def __repr__(self):
        return f'Form: {self.name}, id: {self.form_id}, questions: {self.questions}'

    @classmethod
    def getForm(cls, form_id):
        stmt = SQL('SELECT * FROM "Forms" WHERE form_id = {}').format(
            SQL(',').join(map(sql.Literal, [form_id])),
        )
        return [Form(*el[1:], form_id = el[0]) for el in run_query(stmt)]

    @classmethod
    def addForm(cls, name, questions):
        stmt = SQL('INSERT INTO "Forms" ({}) VALUES ({})').format(
            SQL(',').join(map(sql.Identifier, cls.column_names)),
            SQL(',').join(map(sql.Literal, [name, questions])),
        )
        run_query_nofetch(stmt)

class Question:
    column_names = ['content']

    def __init__(self, content, id = None):
        self.content = content
        self.id = id

    def __repr__(self):
        return f'Question: {self.content}, id: {self.id}'

    @classmethod
    def getQuestion(cls, id):
        stmt = SQL('SELECT * FROM "Questions" WHERE id = {}').format(
            SQL(',').join(map(sql.Literal, [id])),
        )
        return [Question(*el[1:], id = el[0]) for el in run_query(stmt)]
    
    @classmethod
    def addQuestion(cls, content):
        stmt = SQL('INSERT INTO "Questions" ({}) VALUES ({})').format(
            SQL(',').join(map(sql.Identifier, cls.column_names)),
            SQL(',').join(map(sql.Literal, [content])),
        )
        run_query_nofetch(stmt)

class Review:

    column_names = ['user_id', 'q_json', 'form_id', 'lat', 'lon', 'adr', 'place', 'comment', 'mark']
    
    def __init__(self, user_id, q_json, form_id, lat, lon, adr, place, comment, mark, review_id = None):
        self.user_id = user_id
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
        return f'Review: {self.q_json}, by: {self.user_id}, place: {self.place}, comment: {self.comment}, id: {self.review_id}'

    @classmethod
    def getReview(cls, review_id):
        stmt = SQL('SELECT * FROM "Reviews" WHERE review_id = {}').format(
            SQL(',').join(map(sql.Literal, [review_id])),
        )
        return [Review(*el[1:], review_id = el[0]) for el in run_query(stmt)]

    @classmethod
    def addReview(cls, *args, **kwargs):
        stmt = SQL('INSERT INTO "Reviews" ({}) VALUES ({})').format(
            SQL(',').join(map(sql.Identifier, cls.column_names)),
            SQL(',').join(map(sql.Literal, args)),
        )
        run_query_nofetch(stmt)
    

# User.addNewUser(100500, 'Testname', 'TestLastName','chat','unmae')
# print(User.getUser(100500)[0].checkLocation())
print(User.getUser(100500)[0].updateLocation(100, 500))
# print(Object.getObjects())
# print(Object.getPlaceStatus('ONPU'))
# print(Object.getObjects())
# print(User.getUser(100500))
# print(Form.getForm(1))
# print(Form.addForm('TestYForm', [1,2]))
# print(Question.getQuestion(1))
# print(Question.addQuestion('Hellot there?'))
# print(Review.getReview(1))
# print (type(Review.getReview(1)[0].q_json))
# Review.addReview(100500, json.dumps({'1':0}), 1,1,1,'Tereshkovoy10', 'ONPU', 'cmnt', 10)