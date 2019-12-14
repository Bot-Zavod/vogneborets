from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from init import BotInitialize
import logging
from time import sleep
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

# LOGSLOGSLOGS
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

QUEST_1, QUEST_2, QUEST_3, QUEST_4, COMMENT, CONFIRM, CHECK  = range(7)

# Стартовое сообщение
def start_command(update, context):
	sticker = "CAADAgAD_iAAAulVBRgi4A0qOPfBBRYE"
	# Так как несовпадение выбраного места возвращает нас инлайном сюда,
	# то update для инлайна немного другой.
	if update.callback_query:
		update = update.callback_query
		first_name = update.message.chat.first_name
	else:
		first_name = update.effective_chat.first_name

	text = f"*Добрый день, {first_name}!*"
	reply_markup = ReplyKeyboardMarkup([['Оценить заведение'],['Проверить'],['Советы при ЧС']], resize_keyboard=True)
	update.message.reply_sticker(sticker=sticker)
	update.message.reply_text(text=text, reply_markup=reply_markup, parse_mode='markdown')

# Сообщение на команду помощи
def help_command(update, context):
	sticker = "CAADAgADCSEAAulVBRjFPBc0MGnDUhYE"
	update.message.reply_sticker(sticker=sticker)
	text = "*Чем могу помочь?*"
	update.message.reply_text(text=text, parse_mode='markdown')

# Обработка сообщение с геолокацией
def check_location(update, context):
	lon = update.effective_message.location.longitude
	lat = update.effective_message.location.latitude
	update.message.reply_text(text=str(lat)+' '+str(lon), parse_mode='markdown')

# Начало разговора, при оценивании объекта
# Отправляет клавиатуру, которая поможет отправить геолокацию
def check_place(update, context):
	button = KeyboardButton(text="Отправить местоположение", request_location = True)
	reply_markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True)
	text = "*Хорошо, давай оценим место, где ты сейчас находишься.*\nОтправь мне свое метоположение или напиши название заведения!\n/cancel - чтоб остановить"
	update.message.reply_text(text=text, parse_mode='markdown', reply_markup=reply_markup)
	return CONFIRM

# Подтверждаем место для оценивания
def confirm_place(update, context):
	# отсюда вытащим id сообщения для удаления, надо это только для того, чтоб скрыть ненужную клавиатуру
	mess = context.bot.send_message(chat_id=update.effective_chat.id, text='`processing...`', reply_markup=ReplyKeyboardRemove(), parse_mode='markdown')
	context.bot.delete_message(chat_id=mess.chat.id, message_id=mess.message_id)

	# Чтоб правильнее отслеживать ответы, придется везде прописывать 
	# клаву с разными callback_data
	button1 = InlineKeyboardButton('Да ✅', callback_data='yes1')
	button2 = InlineKeyboardButton('Нет ❌', callback_data='no1')
	keyboard = InlineKeyboardMarkup([[button1, button2]])

	text = '*Вы находитесь тут - *'+ update.message.text+' ?'
	update.message.reply_text(text=text, parse_mode='markdown', reply_markup=keyboard)
	return QUEST_1

# ВОПРОСЫ

def q1(update, context):
	query = update.callback_query	
	button1 = InlineKeyboardButton('Да ✅', callback_data='yes2')
	button2 = InlineKeyboardButton('Нет ❌', callback_data='no2')
	keyboard = InlineKeyboardMarkup([[button1, button2]])

	if query.data == 'yes1':
		text = "*Вопрос №1*"
		query.edit_message_text(text=text, parse_mode='markdown', reply_markup=keyboard)
		return QUEST_2
	elif query.data == 'no1':
		text = "*Попробуй еще раз!*"
		query.edit_message_text(text=text, parse_mode='markdown')
		start_command(update, context) # redirect to /start
		return ConversationHandler.END # end of conversation

def q2(update, context):
	query = update.callback_query
	button1 = InlineKeyboardButton('Да ✅', callback_data='yes3')
	button2 = InlineKeyboardButton('Нет ❌', callback_data='no3')
	keyboard = InlineKeyboardMarkup([[button1, button2]])

	# запись в бд будет
	if query.data == 'yes':
		pass
	elif query.data == 'no':
		pass

	text = "*Вопрос №2*"
	query.edit_message_text(text=text, parse_mode='markdown', reply_markup=keyboard)
	return QUEST_3

def q3(update, context):
	query = update.callback_query
	button1 = InlineKeyboardButton('Да ✅', callback_data='yes4')
	button2 = InlineKeyboardButton('Нет ❌', callback_data='no4')
	keyboard = InlineKeyboardMarkup([[button1, button2]])

	if query.data == 'yes':
		pass
	elif query.data == 'no':
		pass

	text = "*Вопрос №3*"
	query.edit_message_text(text=text, parse_mode='markdown', reply_markup=keyboard)
	return QUEST_4

def q4(update, context):
	query = update.callback_query
	button1 = InlineKeyboardButton('Да ✅', callback_data='yes5')
	button2 = InlineKeyboardButton('Нет ❌', callback_data='no5')
	keyboard = InlineKeyboardMarkup([[button1, button2]])

	if query.data == 'yes':
		pass
	elif query.data == 'no':
		pass
	
	text = "*Вопрос №4*"
	query.edit_message_text(text=text, parse_mode='markdown', reply_markup=keyboard)
	return COMMENT


# Обработка комментария после всех вопросов
def comment(update, context):
	query = update.callback_query
	text = "*Оставь комментарий*"
	query.edit_message_text(text=text, parse_mode='markdown')
	return CHECK #переключаемся на чек

#Итог при оценке.
def check_result(update, context):
	text = "*Многие думают так-же!* /start"
	update.message.reply_text(text=text, parse_mode='markdown')
	return ConversationHandler.END #завершение диалога

# команда отмены COnversationHandler
def cancel(update, context):
    user = update.message.from_user
    update.message.reply_text('*Ладно. Закончим с этим)*', parse_mode='markdown')
    start_command(update, context)
    return ConversationHandler.END #завершение диалога

def main():
	# Initialized BOT
	updater, dispatcher = BotInitialize()

	# Start command handler
	dispatcher.add_handler(CommandHandler('start', start_command))

	# Help command handler
	dispatcher.add_handler(CommandHandler('help', help_command))

	# Location handler
	dispatcher.add_handler(MessageHandler(Filters.location, check_location))

	# Создаем Ветку диалога по оценке заведения. Во время диалога работает /start, а лучше бы не работал
	# создает только лишние проблемы. Так как вызывает баги
	checkPlace_handler = ConversationHandler(
		entry_points=[MessageHandler(Filters.regex('Оценить заведение'), check_place)],

		states={
			# Путь развития диалога, Сначала адресс(выше на 2 строки), потом
			# Проверка адреса, если не то, то закрыает. Если все норм, то 
			# начинает задавтаь вопросы, а там и комментарий в конце. В итоге
			# CHECK в конце будет записывать комментарий и показывать оценку места для других и 
			# другие похожие комментарии пользователя
			CONFIRM: [MessageHandler(Filters.text, confirm_place)],
			QUEST_1: [CallbackQueryHandler(q1)],
			QUEST_2: [CallbackQueryHandler(q2)],
			QUEST_3: [CallbackQueryHandler(q3)],
			QUEST_4: [CallbackQueryHandler(q4)],
			COMMENT: [CallbackQueryHandler(comment)],
			CHECK: [MessageHandler(Filters.text, check_result)]
		},
		# команда которая заканчивает диалог когда угодно /cancel
		fallbacks=[CommandHandler('cancel', cancel)]
	)

	dispatcher.add_handler(checkPlace_handler)

	updater.start_polling()	



if __name__ == "__main__":
	main()