import psycopg2
from contextlib import closing
from psycopg2.extras import DictCursor
from psycopg2.sql import SQL 
from psycopg2 import sql
import credentials

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

class Object:
    def __init__(self, name, lat, lon, id = None):
        #id is present in objects, returned by query, in your objects is None
        self.name = name
        self.lat = lat
        self.lon = lon
        self.id = id

    def __repr__(self):
        return f'Object: {self.name} at {self.lat}, {self.lon}'
        
    @classmethod
    def getObjects(cls):
        return [Object(*el[1:], id = el[0]) for el in run_query(SQL('SELECT * FROM "Objects"'))]

    @classmethod
    def getPlaceStatus(cls, name):
        stmt = SQL('''SELECT AVG(result) FROM ("Questions" 
                      INNER JOIN "Reviews" on "Questions".review_id = "Reviews".review_id) 
                      INNER JOIN "Objects" ON "Reviews".object_id = "Objects".object_id 
                      WHERE "Objects".name = {};''').format(sql.Literal(name))
        print(run_query(stmt))
        

class User:

    column_names = ['chat_id', 'first_name', 'last_name', 'username', 'mode']

    def __init__(self, chat_id ,first_name,last_name, username, mode, user_id = None):
        self.chat_id = chat_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.mode = mode
        self.user_id = user_id

    def __repr__(self):
        return f'User: {self.username}, mode: {self.mode}, chat_id: {self.chat_id}'

    @classmethod
    def addNewUser(cls, chat_id, first_name, last_name, username, mode):
        stmt = SQL('INSERT INTO "Users" ({}) VALUES ({})').format(
            SQL(',').join(map(sql.Identifier, cls.column_names)),
            SQL(',').join(map(sql.Literal, [chat_id, first_name, last_name, username, mode])),
        )
        run_query_nofetch(stmt)



# User.addNewUser(100500, 'Testname', 'TestLastName','chat','unmae')
# print(Object.getObjects())
# print(Object.getPlaceStatus('ONPU'))
# print(Object.getObjects())