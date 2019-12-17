from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from GeoReverse import CoordinatesToAdress
from init import BotInitialize
from time import sleep
from ActiveUsers import *
import logging


# LOGSLOGSLOGS
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# iMITATE USER_db
# QUEST_1, QUEST_2, QUEST_3, QUEST_4, COMMENT, FINISH = range(6)

QUESTIONS = ['Ты пацан?', 'Завтра утром ты будешь кушать кашу?', 'У тебя собака есть?', 'Ты умный парень?']
ANSWERS = []

# Active users list. Users.allUsers() - to show all Users
Users = Users()

# start message
def start_command(update, context):	
	first_name = update.message.chat.first_name	
	chat_id = update.message.chat.id
	sticker = "CAADAgAD_iAAAulVBRgi4A0qOPfBBRYE"

	# Check user mode for correct menu
	if Users.getUser(chat_id) and Users.getUser(chat_id)['status']:
		text = f"*Добрый день, {first_name}!*\n\nРады вас видеть! Выберите действие из меню ниже."
		reply_markup = ReplyKeyboardMarkup([['Оценить заведение'],['Проверить'],['Советы при ЧС']], resize_keyboard=True)
	else:
		# add new User
		Users.addUser(chat_id, first_name)
		text = f"*Добрый день, {first_name}!*\n\nОтправьте нам свое местоположение, тоб мы могли провести оценку места"
		location_button = KeyboardButton(text="Отправить местоположение", request_location = True)
		reply_markup = ReplyKeyboardMarkup([[location_button],['Советы при ЧС']], resize_keyboard=True)
	
	logger.info("User %s: send /start command", update.message.chat.id)
	update.message.reply_sticker(sticker=sticker)
	update.message.reply_text(text=text, reply_markup=reply_markup, parse_mode='markdown')

# Instructions during emergency situations 
def Instructions(update, context):
	# add User if he is absent, return False if absent
	Users.addUser(update.message.chat.id, update.message.chat.first_name)
	logger.info("User %s: ask instructions", update.message.chat.id)
	update.message.reply_text(text='*Инструкции при пожаре и других ЧС!*', parse_mode='markdown')

def test(update, context):
	print(Users.allUsers())
	update.message.reply_text(text='Читайте логи', parse_mode='markdown')


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
		update.message.reply_text(text='*В каком именно заведении вы находитесь?*', reply_markup=reply_markup, parse_mode='markdown')
		# add places to Users
		Users.changePlacesVariant(chat_id, PLACES_VARIANT)

		# Submit the correct location
		reg = '^'+'|'.join(PLACES_VARIANT)+'$'
		logger.info("User %s: send location %s", update.message.chat.id, str(lat)+','+str(lon))
		dispatcher.add_handler(MessageHandler(Filters.regex(reg), submit_location))
	else:
		update.message.reply_text(text='*Что-то я ничего не вижу. Попробуй еще раз!*', parse_mode='markdown')

	


# Submit location and turn True mode on User
def submit_location(update, context):
	chat_id = update.message.chat.id
	msg = update.effective_message.text

	# check user mode and correct it
	if msg in Users.getUser(chat_id)['PLACES_VARIANT'] and Users.getUser(chat_id)['status']==False:		
		Users.changeUserStatus(chat_id, True)	
		Users.changeUserPlace(chat_id, msg)

		text = f'`{update.effective_message.text}`\n\n*Давай теперь оценим его! Для этого тебе надо будет ответить на несколько вопросов. Или ты можешь узнать, что другие думаю про это место*'
		reply_markup = ReplyKeyboardMarkup([['Оценить заведение'],['Проверить'],['Советы при ЧС']], resize_keyboard=True)
		logger.info("User %s: submit location '%s' ", update.message.chat.id, Users.getUser(chat_id)['USER_PLACE'])
		update.message.reply_text(text=text, reply_markup=reply_markup, parse_mode='markdown')

# True mode--- place info
def place_find_output(update, context):
	chat_id = update.message.chat.id
	if Users.getUser(chat_id) and Users.getUser(chat_id)['status']:
		logger.info("User %s: ask '%s' place info.", chat_id, Users.getUser(chat_id)['USER_PLACE'])
		update.message.reply_text(text=f"Вот все, что у меня есть про это место: { Users.getUser(chat_id)['USER_PLACE'] }", parse_mode='markdown')

# True mode--- lets estimate place
def place_estimation(update, context):
	chat_id = update.message.chat.id
	if Users.getUser(chat_id) and Users.getUser(chat_id)['status']:
		logger.info("User %s: started estimate '%s' place ", chat_id, Users.getUser(chat_id)['USER_PLACE'])
		update.message.reply_text(text=f"*Давай оценим: { Users.getUser(chat_id)['USER_PLACE'] }*\n\n Ответь на вопросы ниже!", parse_mode='markdown')

		# sending a question
		for question_text, i in enumerate(QUESTIONS):
			questions(update, context, question_text)
			dispatcher.add_handler(CallbackQueryHandler(answer))


def questions(update, context, question_text):
	button1 = InlineKeyboardButton('Да ✅', callback_data='yes')
	button2 = InlineKeyboardButton('Нет ❌', callback_data='no')
	button3 = InlineKeyboardButton('Не знаю ❔', callback_data='i dont know')
	keyboard = InlineKeyboardMarkup([[button1, button2],[button3]])
	update.message.reply_text(text=question_text, parse_mode='markdown', reply_markup=keyboard)
	dispatcher.add_handler(CallbackQueryHandler(answer))


def answer(update, context):
	query = update.callback_query
	context.bot.delete_message(query.message.chat.id, query.message.message_id)
	print('message_id',query.message.message_id,':',query.message.text,' - ',query.data)




if __name__ == "__main__":
	# Initialized BOT
	updater, dispatcher = BotInitialize()

	# Start command handler
	dispatcher.add_handler(CommandHandler('start', start_command))

	# test command
	dispatcher.add_handler(CommandHandler('test', test))

	# Instructions and Tips
	dispatcher.add_handler(MessageHandler(Filters.regex('^Советы при ЧС$'), Instructions))

	# Location handler
	dispatcher.add_handler(MessageHandler(Filters.location, check_location))

	# # True mode--- place info
	dispatcher.add_handler(MessageHandler(Filters.regex('^Проверить$'), place_find_output))

	dispatcher.add_handler(MessageHandler(Filters.regex('^Оценить заведение$'), place_estimation))

	# For more comfortable start and stop from console
	updater.start_polling()	
	updater.idle()