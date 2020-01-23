from os import environ

def init():
	# Passing all needed secure data to enviromental variables
	environ['bot_token'] = '832853209:AAG7skNPCoj5X0Ky4HHEwvqnw4RIw3pT-r0'

	environ['google_key'] = 'AIzaSyBrQmgLCVlaxO4hGtPlJAzeXE8U7xdufWQ'

	environ['db_name'] = 'Vogneborets'
	environ['db_user'] = 'postgres'
	environ['db_password'] = 'Vogneborets228'
	environ['db_host'] = 'vogneborets-db.ckvhezxgjq9a.us-west-2.rds.amazonaws.com'
	environ['db_port'] = '5432'