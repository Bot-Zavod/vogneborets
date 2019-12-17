from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from init import BotInitialize
import logging
from time import sleep
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from GeoReverse import CoordinatesToAdress

# LOGSLOGSLOGS
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# iMITATE USER_db
IS_USER_ACTIVE = False
PLACES_VARIANT = []
USER_PLACE = ''
QUEST_1, QUEST_2, QUEST_3, QUEST_4, COMMENT, FINISH = range(6)




# start message
def start_command(update, context):	
	first_name = update.message.chat.first_name	
	sticker = "CAADAgAD_iAAAulVBRgi4A0qOPfBBRYE"

	# Check user mode for correct menu
	if IS_USER_ACTIVE:
		text = f"*Добрый день, {first_name}!*\n\nРады вас видеть! Выберите действие из меню ниже."
		reply_markup = ReplyKeyboardMarkup([['Оценить заведение'],['Проверить'],['Советы при ЧС']], resize_keyboard=True)
	else:
		text = f"*Добрый день, {first_name}!*\n\nОтправьте нам свое местоположение, тоб мы могли провести оценку места"
		location_button = KeyboardButton(text="Отправить местоположение", request_location = True)
		reply_markup = ReplyKeyboardMarkup([[location_button],['Советы при ЧС']], resize_keyboard=True)
	
	logger.info("User %s: send /start command", update.message.chat.id)
	update.message.reply_sticker(sticker=sticker)
	update.message.reply_text(text=text, reply_markup=reply_markup, parse_mode='markdown')

# Instructions during emergency situations 
def Instructions(update, context):
	logger.info("User %s: ask instructions", update.message.chat.id)
	update.message.reply_text(text='*Инструкции при пожаре и других ЧС!*', parse_mode='markdown')

# Location message
def check_location(update, context):
	lon = update.effective_message.location.longitude
	lat = update.effective_message.location.latitude
	res = CoordinatesToAdress(str(lat)+','+str(lon))
	if len(res) > 0:
		buttons = []
		global PLACES_VARIANT
		for x in res:
			buttons.append([x['name']])
			PLACES_VARIANT.append(x['name'])
		reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
		update.message.reply_text(text='*В каком именно заведении вы находитесь?*', reply_markup=reply_markup, parse_mode='markdown')
	else:
		update.message.reply_text(text='*Что-то я ничего не вижу. Попробуй еще раз!*', parse_mode='markdown')

	# Submit the correct location
	reg = '^'+'|'.join(PLACES_VARIANT)+'$'
	logger.info("User %s: send location %s", update.message.chat.id, str(lat)+','+str(lon))
	dispatcher.add_handler(MessageHandler(Filters.regex(reg), submit_location))


# Submit location and turn True mode on User
def submit_location(update, context):
	msg = update.effective_message.text
	# check user mode and correct it
	global USER_PLACE
	global IS_USER_ACTIVE
	if msg in PLACES_VARIANT and IS_USER_ACTIVE==False:		
		IS_USER_ACTIVE = True
		USER_PLACE = msg
		text = f'`{update.effective_message.text}`\n\n*Давай теперь оценим его! Для этого тебе надо будет ответить на несколько вопросов. Или ты можешь узнать, что другие думаю про это место*'
		reply_markup = ReplyKeyboardMarkup([['Оценить заведение'],['Проверить'],['Советы при ЧС']], resize_keyboard=True)
		logger.info("User %s: submit location '%s' ", update.message.chat.id, USER_PLACE)
		update.message.reply_text(text=text, reply_markup=reply_markup, parse_mode='markdown')

# True mode--- place info
def place_find_output(update, context):
	if IS_USER_ACTIVE:
		logger.info("User %s: ask '%s' place info.", update.message.chat.id, USER_PLACE)
		update.message.reply_text(text=f'Вот все, что у меня есть про это место: {USER_PLACE}', parse_mode='markdown')

# True mode--- lets estimate place
def place_estimation(update, context):
	if IS_USER_ACTIVE:
		logger.info("User %s: started estimate '%s' place ", update.message.chat.id, USER_PLACE)
		update.message.reply_text(text=f'*Давай оценим: {USER_PLACE}*\n\n Ответь на вопросы ниже!', parse_mode='markdown')
		q1(update, context)







# QUESTIONS

def q1(update, context):
	button1 = InlineKeyboardButton('Да ✅', callback_data='yes2')
	button2 = InlineKeyboardButton('Нет ❌', callback_data='no2')
	keyboard = InlineKeyboardMarkup([[button1, button2]])
	text = "*Вопрос №1*"
	update.message.reply_text(text=text, parse_mode='markdown', reply_markup=keyboard)
	return QUEST_2

def q2(update, context):
	query = update.callback_query
	button1 = InlineKeyboardButton('Да ✅', callback_data='yes3')
	button2 = InlineKeyboardButton('Нет ❌', callback_data='no3')
	keyboard = InlineKeyboardMarkup([[button1, button2]])

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
	keyboard = InlineKeyboardMarkup([[button1, button2]])

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
	keyboard = InlineKeyboardMarkup([[button1, button2]])

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
    update.message.reply_text(text='Пока!',  reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


if __name__ == "__main__":
	# Initialized BOT
	updater, dispatcher = BotInitialize()

	# Start command handler
	dispatcher.add_handler(CommandHandler('start', start_command))

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
				QUEST_2: [CallbackQueryHandler(q2)],
				QUEST_3: [CallbackQueryHandler(q3)],
				QUEST_4: [CallbackQueryHandler(q4)],
				COMMENT: [CallbackQueryHandler(comment)],
				FINISH: [MessageHandler(Filters.text, finish_est)]
			},
			fallbacks=[CommandHandler('cancel', cancel)]
		))


	updater.start_polling()	
	updater.idle()