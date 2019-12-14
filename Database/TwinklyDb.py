import psycopg2
from contextlib import closing
from psycopg2.extras import DictCursor
from psycopg2.sql import SQL 
from psycopg2 import sql 


dbname = 'Twinkly'
user = 'twinklyadmin'
password = 'tfEJQjqS8wYvH23xEcGH'
host = 'twinkly-dev.cc4xdtflaafw.us-west-2.rds.amazonaws.com'

def run_query(stmt):
    with closing(psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=5433)) as conn:
        with conn.cursor() as cursor:
            cursor.execute(stmt)
            conn.commit()
            return cursor.fetchall()

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
print(Object.getObjects())