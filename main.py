from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from init import BotInitialize
import logging
from time import sleep
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
import re

# LOGSLOGSLOGS
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

QUEST_1, QUEST_2, QUEST_3, QUEST_4, COMMENT = range(5)

def start_command(update, context):
	sticker = "CAADAgAD_iAAAulVBRgi4A0qOPfBBRYE"
	text = f"*Добрый день, {update.effective_chat.first_name}!*"
	reply_markup = ReplyKeyboardMarkup([['Оценить заведение'],['Проверить'],['Советы при ЧС']], resize_keyboard=True)
	update.message.reply_sticker(sticker=sticker)
	update.message.reply_text(text=text, reply_markup=reply_markup, parse_mode='markdown')


def help_command(update, context):
	sticker = "CAADAgADCSEAAulVBRjFPBc0MGnDUhYE"
	update.message.reply_sticker(sticker=sticker)
	text = "*Чем могу помочь?*"
	update.message.reply_text(text=text, parse_mode='markdown')


def check_location(update, context):
	lon = update.effective_message.location.longitude
	lat = update.effective_message.location.latitude
	update.message.reply_text(text=str(lon)+' '+str(lat), parse_mode='markdown')


def test(update, context):
	# Inline Keyboard test#1
	button1 = InlineKeyboardButton('кнопка1', callback_data='1')
	button2 = InlineKeyboardButton('кнопка2', callback_data='2')
	button3 = InlineKeyboardButton('кнопка3', callback_data='3')
	button4 = InlineKeyboardButton('кнопка4', callback_data='4')
	keyboard = InlineKeyboardMarkup([[button1, button2],[button3, button4]])
	update.message.reply_text(text='InlineKeyboard test#1', reply_markup=keyboard)

	# Check message
	text2 = "ЧТО ЭТО ТАКОЕ? *<"+update.message.text.upper()+'>*'
	update.message.reply_text(text=text2, parse_mode='markdown')

	print(type(update.effective_chat.id))




def check_place(update, context):
	button = KeyboardButton(text="Отправить местоположение", request_location = True)
	reply_markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True)
	text = "*Хорошо, давай оценим место, где ты сейчас находишься.*\nОтправь мне свое метоположение или напиши название заведения!\n/cancel - чтоб остановить"
	update.message.reply_text(text=text, parse_mode='markdown', reply_markup=reply_markup)
	return QUEST_1

def q1(update, context):
	text = "*Вопрос №1*"
	update.message.reply_text(text=text, parse_mode='markdown')
	return QUEST_2

def q2(update, context):
	text = "*Вопрос №2*"
	update.message.reply_text(text=text, parse_mode='markdown')
	return QUEST_3

def q3(update, context):
	text = "*Вопрос №3*"
	update.message.reply_text(text=text, parse_mode='markdown')
	return QUEST_4

def q4(update, context):
	text = "*Вопрос №4*"
	update.message.reply_text(text=text, parse_mode='markdown')
	return COMMENT

def comment(update, context):
	text = "*Оставь комментарий*"
	update.message.reply_text(text=text, parse_mode='markdown')
	start_command(update, context)
	return ConversationHandler.END

def cancel(update, context):
    user = update.message.from_user
    update.message.reply_text('*Ладно. Закончим с этим)*', parse_mode='markdown')
    start_command(update, context)
    return ConversationHandler.END

def main():
	# Initialized BOT
	updater, dispatcher = BotInitialize()

	# Start command handler
	dispatcher.add_handler(CommandHandler('start', start_command))

	# Help command handler
	dispatcher.add_handler(CommandHandler('help', help_command))

	# Test commant handler
	dispatcher.add_handler(CommandHandler('test', test))

	# Location handler
	dispatcher.add_handler(MessageHandler(Filters.location, check_location))

	# Check Object Handler ----
	CHECK_handler = ConversationHandler(
		entry_points=[CommandHandler('check', check_place), MessageHandler(Filters.regex('Оценить заведение'), check_place)],

		states={
			QUEST_1: [MessageHandler(Filters.text, q1)],
			QUEST_2: [MessageHandler(Filters.text, q2)],
			QUEST_3: [MessageHandler(Filters.text, q3)],
			QUEST_4: [MessageHandler(Filters.text, q4)],
			COMMENT: [MessageHandler(Filters.text, comment)],
		},
		fallbacks=[CommandHandler('cancel', cancel)]
	)

	dispatcher.add_handler(CHECK_handler)

	updater.start_polling()	



if __name__ == "__main__":
	main()