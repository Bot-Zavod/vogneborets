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
QUEST_1, QUEST_2, QUEST_3, QUEST_4, COMMENT, FINISH = range(6)

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
		return QUEST_1




# QUESTIONS

def q1(update, context):
	button1 = InlineKeyboardButton('Да ✅', callback_data='yes2')
	button2 = InlineKeyboardButton('Нет ❌', callback_data='no2')
	button3 = InlineKeyboardButton('Не знаю ❔', callback_data='wtf2')
	keyboard = InlineKeyboardMarkup([[button1, button2],[button3]])
	text = "*Вопрос №1*"
	update.message.reply_text(text=text, parse_mode='markdown', reply_markup=keyboard)
	return QUEST_2





def q2(update, context):
	query = update.callback_query
	button1 = InlineKeyboardButton('Да ✅', callback_data='yes3')
	button2 = InlineKeyboardButton('Нет ❌', callback_data='no3')
	button3 = InlineKeyboardButton('Не знаю ❔', callback_data='wtf3')
	keyboard = InlineKeyboardMarkup([[button1, button2],[button3]])
	# запись в бд будет
	if query.data == 'yes2':
		pass
	elif query.data == 'no2':
		pass

	text = "*Вопрос №2*"
	query.edit_message_text(text=text, parse_mode='markdown', reply_markup=keyboard)
	return QUEST_3

def q3(update, context):
	query = update.callback_query
	button1 = InlineKeyboardButton('Да ✅', callback_data='yes4')
	button2 = InlineKeyboardButton('Нет ❌', callback_data='no4')
	button3 = InlineKeyboardButton('Не знаю ❔', callback_data='wtf4')
	keyboard = InlineKeyboardMarkup([[button1, button2],[button3]])

	if query.data == 'yes3':
		pass
	elif query.data == 'no3':
		pass

	text = "*Вопрос №3*"
	query.edit_message_text(text=text, parse_mode='markdown', reply_markup=keyboard)
	return QUEST_4

def q4(update, context):
	query = update.callback_query
	button1 = InlineKeyboardButton('Да ✅', callback_data='yes5')
	button2 = InlineKeyboardButton('Нет ❌', callback_data='no5')
	button3 = InlineKeyboardButton('Не знаю ❔', callback_data='wtf5')
	keyboard = InlineKeyboardMarkup([[button1, button2],[button3]])

	if query.data == 'yes4':
		pass
	elif query.data == 'no4':
		pass
	
	text = "*Вопрос №4*"
	query.edit_message_text(text=text, parse_mode='markdown', reply_markup=keyboard)
	return COMMENT

# Comment by user
def comment(update, context):
	query = update.callback_query
	if query.data == 'yes4':
		pass
	elif query.data == 'no4':
		pass
	text = "*Оставь комментарий*"
	query.edit_message_text(text=text, parse_mode='markdown')
	return FINISH

# Write the Users comment and end the ConversationHandler
def finish_est(update, context):
	text = "*Вот похожие отзывы: *"
	update.message.reply_text(text=text, parse_mode='markdown')
	return ConversationHandler.END









# End commant of ConversationHandler
def cancel(update, context):
	chat_id = update.message.chat.id
	logger.info("User %s: end estimate '%s' by /cansel command ", chat_id, Users.getUser(chat_id)['USER_PLACE'])
	update.message.reply_text(text='Ты можешь попытаться еще раз!',  reply_markup=ReplyKeyboardRemove())
	return ConversationHandler.END


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

	# ConversationHandler for ESTIMATE place by User
	dispatcher.add_handler(ConversationHandler(
			entry_points=[MessageHandler(Filters.regex('^Оценить заведение$'), place_estimation)],
			states={
				QUEST_1: [CallbackQueryHandler(q1)],
				QUEST_2: [CallbackQueryHandler(q2)],
				QUEST_3: [CallbackQueryHandler(q3)],
				QUEST_4: [CallbackQueryHandler(q4)],
				COMMENT: [CallbackQueryHandler(comment)],
				FINISH: [MessageHandler(Filters.text, finish_est)]
			},
			fallbacks=[CommandHandler('cancel', cancel)]
		))

	# Sort all messanges and check User in botUsers
	# dispatcher.add_handler(MessageHandler(Filters.all, sorter))


	# For more comfortable start and stop from console
	updater.start_polling()	
	updater.idle()