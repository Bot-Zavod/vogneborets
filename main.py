from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from GeoReverse import CoordinatesToAdress
from init import BotInitialize
from time import sleep
from ActiveUsers import *
import logging
import threading 


# LOGSLOGSLOGS
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Active users list. Users.allUsers() - to show all Users
Users = Users()

# autodeleting depricated users
def autodeleting():
	while True:
		sleep(30) # Wait 30 sec
		us = Users.getOldUsers()
		for x in us:
			Users.delete_user(x)
			print(f'User {x}: deleted from memory')

# start thread
thread = threading.Thread(target=autodeleting)
thread.start()

# Texts to bot

# start message
def start_command(update, context):	
	first_name = update.message.chat.first_name	
	chat_id = update.message.chat.id
	sticker = "CAADAgAD_iAAAulVBRgi4A0qOPfBBRYE"

	# Check user mode for correct menu
	if Users.getUser(chat_id) and Users.getUser(chat_id)['status']:
		text = f"*Добрый день, {first_name}!*\n\nРады вас видеть! Выберите действие из меню ниже."
		button1 = 'Оценить заведение'
		button2 = 'Проверить'
		button3 = 'Советы при ЧС'
		reply_markup = ReplyKeyboardMarkup([[button1],[button2],[button3]], resize_keyboard=True)
	else:
		# add new User
		Users.addUser(chat_id, first_name)
		text = f"*Добрый день, {first_name}!*\n\nОтправьте нам свое местоположение, тоб мы могли провести оценку места"
		location_button_text = "Отправить местоположение"
		button = 'Советы при ЧС'
		location_button = KeyboardButton(text=location_button_text, request_location = True)
		reply_markup = ReplyKeyboardMarkup([[location_button],[button]], resize_keyboard=True)
	
	logger.info("User %s: send /start command", update.message.chat.id, )
	update.message.reply_sticker(sticker=sticker)
	update.message.reply_text(text=text, reply_markup=reply_markup, parse_mode='markdown')

	# -----------Update User Activity--------------
	Users.update_last_activity(chat_id)

# Instructions during emergency situations 
def Instructions(update, context):
	# add User if he is absent, return False if absent
	Users.addUser(update.message.chat.id, update.message.chat.first_name)
	logger.info("User %s: ask instructions", update.message.chat.id)
	text = '*Инструкции при пожаре и других ЧС!*'
	update.message.reply_text(text=text, parse_mode='markdown')

def test(update, context):
	print(Users.allUsers())
	text = 'Читайте логи'
	update.message.reply_text(text=text, parse_mode='markdown')

# Location message
def check_location(update, context):
	chat_id = update.message.chat.id
	lon = update.effective_message.location.longitude
	lat = update.effective_message.location.latitude
	res = CoordinatesToAdress(str(lat)+','+str(lon))
	# add User if he is absent, return False if absent
	Users.addUser(chat_id, update.message.chat.first_name)

	if len(res) > 0:
		buttons = []
		PLACES_VARIANT = []
		for x in res:
			buttons.append([x['name']])
			PLACES_VARIANT.append(x['name'])

		reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
		text = '*В каком именно заведении вы находитесь?*'
		update.message.reply_text(text=text, reply_markup=reply_markup, parse_mode='markdown')
		# add places to Users
		Users.changePlacesVariant(chat_id, PLACES_VARIANT)

		# Submit the correct location
		reg = '^'+'|'.join(PLACES_VARIANT)+'$'
		logger.info("User %s: send location %s", update.message.chat.id, str(lat)+','+str(lon))
		dispatcher.add_handler(MessageHandler(Filters.regex(reg), submit_location))

	else:
		text = '*Что-то я ничего не вижу. Попробуй еще раз!*'
		update.message.reply_text(text=text, parse_mode='markdown')

	# -----------Update User Activity--------------
	Users.update_last_activity(chat_id)

# Submit location and turn True mode on User
def submit_location(update, context):
	chat_id = update.message.chat.id
	msg = update.effective_message.text

	# check user mode and correct it
	if msg in Users.getUser(chat_id)['PLACES_VARIANT'] and Users.getUser(chat_id)['status']==False:		
		Users.changeUserStatus(chat_id, True)	
		Users.changeUserPlace(chat_id, msg)

		text = f'`{update.effective_message.text}`\n\n*Давай теперь оценим его! Для этого тебе надо будет ответить на несколько вопросов. Или ты можешь узнать, что другие думаю про это место*'
		button1 = 'Оценить заведение'
		button2 = 'Проверить'
		button3 = 'Советы при ЧС'
		reply_markup = ReplyKeyboardMarkup([[button1],[button2],[button3]], resize_keyboard=True)
		logger.info("User %s: submit location '%s' ", update.message.chat.id, Users.getUser(chat_id)['USER_PLACE'])
		update.message.reply_text(text=text, reply_markup=reply_markup, parse_mode='markdown')

	# -----------Update User Activity--------------
	Users.update_last_activity(chat_id)

# True mode--- place info
def place_find_output(update, context):
	chat_id = update.message.chat.id
	if Users.getUser(chat_id) and Users.getUser(chat_id)['status']:
		logger.info("User %s: ask '%s' place info.", chat_id, Users.getUser(chat_id)['USER_PLACE'])
		text = f"Вот все, что у меня есть про это место: { Users.getUser(chat_id)['USER_PLACE'] }"
		update.message.reply_text(text=text, parse_mode='markdown')

	# -----------Update User Activity--------------
	Users.update_last_activity(chat_id)

# True mode--- lets estimate place
def place_estimation(update, context):
	chat_id = update.message.chat.id
	if Users.getUser(chat_id) and Users.getUser(chat_id)['status'] and Users.getUser(chat_id)['ACTIVE_QUESTION'] != '':
		logger.info("User %s: started estimate '%s' place ", chat_id, Users.getUser(chat_id)['USER_PLACE'])
		text = f"*Давай оценим: { Users.getUser(chat_id)['USER_PLACE'] }*\n\nОтветь на вопросы ниже!"
		update.message.reply_text(text=text, parse_mode='markdown')

		# send questions messanges
		QUESTIONS = Users.getUser(chat_id)['QUESTIONS']
		ACTIVE_QUESTION = Users.getUser(chat_id)['ACTIVE_QUESTION']
		question_text = QUESTIONS[ACTIVE_QUESTION]
		question(update, context, question_text)

	else:
		text = "*Вы уже оценивали это место!*"
		update.message.reply_text(text=text, parse_mode='markdown')

	# -----------Update User Activity--------------
	Users.update_last_activity(chat_id)


def question(update, context, question_text):
	if update.callback_query:
		update = update.callback_query
	
	chat_id = update.message.chat.id
	button1 = InlineKeyboardButton('Да ✅', callback_data='yes')
	button2 = InlineKeyboardButton('Нет ❌', callback_data='no')
	button3 = InlineKeyboardButton('Не знаю ❔', callback_data='i dont know')
	keyboard = InlineKeyboardMarkup([[button1, button2],[button3]])

	update.message.reply_text(text=question_text, parse_mode='markdown', reply_markup=keyboard)
	Users.uppActiveQuestion(chat_id)

	# -----------Update User Activity--------------
	Users.update_last_activity(chat_id)

def answer(update, context):
	query = update.callback_query
	chat_id = query.message.chat.id
	context.bot.delete_message(query.message.chat.id, query.message.message_id)
	print('message_id',query.message.message_id,':',query.message.text,' - ',query.data)

	Users.addAnswer(chat_id, query.data)
	ACTIVE_QUESTION = Users.getUser(chat_id)['ACTIVE_QUESTION']

	if ACTIVE_QUESTION == 'comment':
		dispatcher.add_handler(MessageHandler(Filters.text, check_comment))
		text = '*Оставьте комментарий!*'
		context.bot.send_message(query.message.chat.id, text=text, parse_mode='markdown', reply_markup=ReplyKeyboardRemove())
	else:
		QUESTIONS = Users.getUser(chat_id)['QUESTIONS']
		question_text = QUESTIONS[ACTIVE_QUESTION]
		question(update, context, question_text)

	# -----------Update User Activity--------------
	Users.update_last_activity(chat_id)

def check_comment(update, context):
	chat_id = update.message.chat.id
	Users.addComment(chat_id, update.message.text)
	text = '*Спасибо вам за отзыв!\n\nВот похожие...*'
	button1 = 'Оценить заведение'
	button2 = 'Проверить'
	button3 = 'Советы при ЧС'
	reply_markup = ReplyKeyboardMarkup([[button1],[button2],[button3]], resize_keyboard=True)
	update.message.reply_text(text=text, parse_mode='markdown', reply_markup=reply_markup)

	# -----------Update User Activity--------------
	Users.update_last_activity(chat_id)

def change_lang(update, context):
	question_text = '*Выбери язык:*'
	button1 = InlineKeyboardButton('Русский 🇷🇺', callback_data='ru')
	button2 = InlineKeyboardButton('Украинский 🇺🇦', callback_data='ua')
	button3 = InlineKeyboardButton('English 🇺🇸', callback_data='en')
	keyboard = InlineKeyboardMarkup([[button1], [button2], [button3]])

	update.message.reply_text(text=question_text, parse_mode='markdown', reply_markup=keyboard)

def select_lang(update, context):
	query = update.callback_query.message
	context.bot.delete_message(query.chat.id, query.message_id)
	text = 'Хороший выбор!'
	update.callback_query.message.reply_text(text=text, parse_mode='markdown')


if __name__ == "__main__":
	# Initialized BOT
	updater, dispatcher = BotInitialize()

	# Start command handler
	dispatcher.add_handler(CommandHandler('start', start_command))

	# test command
	dispatcher.add_handler(CommandHandler('test', test))

	# change language
	dispatcher.add_handler(CommandHandler('change_lang', change_lang))

	# Instructions and Tips
	dispatcher.add_handler(MessageHandler(Filters.regex('^Советы при ЧС$'), Instructions))

	# Location handler
	dispatcher.add_handler(MessageHandler(Filters.location, check_location))

	# # True mode--- place info
	dispatcher.add_handler(MessageHandler(Filters.regex('^Проверить$'), place_find_output))

	dispatcher.add_handler(MessageHandler(Filters.regex('^Оценить заведение$'), place_estimation))

	dispatcher.add_handler(CallbackQueryHandler(select_lang, pattern='^(ru|ua|en)$'))

	# for write answers
	dispatcher.add_handler(CallbackQueryHandler(answer))



	# For more comfortable start and stop from console
	updater.start_polling()	
	updater.idle()

