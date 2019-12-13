from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from init import BotInitialize
import logging
from time import sleep
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup


def start_command(update, context):
	sticker = "CAADAgAD_iAAAulVBRgi4A0qOPfBBRYE"
	text = f"*Добрый день, {update.effective_chat.first_name}!*"
	button1 = KeyboardButton(text="Проверить место")
	button2 = KeyboardButton(text="Отправить местоположение", request_location = True)
	button3 = KeyboardButton(text="Советы при пожаре")	
	reply_markup = ReplyKeyboardMarkup([[button1],[button2],[button3]])
	context.bot.sendSticker(chat_id=update.effective_chat.id, sticker=sticker)
	context.bot.sendMessage(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup, parse_mode='markdown')


def help_command(update, context):
	sticker = "CAADAgADCSEAAulVBRjFPBc0MGnDUhYE"
	context.bot.sendSticker(chat_id=update.effective_chat.id, sticker=sticker)
	text = "*Чем могу помочь?*"
	context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)


def unknown(update, context):
	text = "*Я вас не понимаю!(*"
	context.bot.sendMessage(chat_id=update.effective_chat.id, text=text, parse_mode='markdown')


def check_location(update, context):
	lon = update.effective_message.location.longitude
	lat = update.effective_message.location.latitude
	context.bot.sendMessage(chat_id=update.effective_chat.id, text=str(lon)+' '+str(lat))


def test(update, context):
	# Inline Keyboard test#1
	button1 = InlineKeyboardButton('кнопка1', callback_data='1')
	button2 = InlineKeyboardButton('кнопка2', callback_data='2')
	button3 = InlineKeyboardButton('кнопка3', callback_data='3')
	button4 = InlineKeyboardButton('кнопка4', callback_data='4')
	keyboard = InlineKeyboardMarkup([[button1, button2],[button3, button4]])
	context.bot.sendMessage(chat_id=update.effective_chat.id, text='InlineKeyboard test#1', reply_markup=keyboard)

	# Check message
	text2 = "ЧТО ЭТО ТАКОЕ? *<"+update.message.text.upper()+'>*'
	context.bot.sendMessage(chat_id=update.effective_chat.id, text=text2, parse_mode='markdown')



if __name__ == "__main__":
	logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

	# Initialized
	updater, dispatcher = BotInitialize()

	# Start command handler
	start_handler = CommandHandler('start', start_command)
	dispatcher.add_handler(start_handler)

	# Help command handler
	help_handler = CommandHandler('help', help_command)
	dispatcher.add_handler(help_handler)

	# Test commant handler
	test = CommandHandler('test', test)
	dispatcher.add_handler(test)

	# Message Handler. Now for test
	unknown_handler = MessageHandler(Filters.text, unknown)
	dispatcher.add_handler(unknown_handler)

	# Location handler
	location_handler = MessageHandler(Filters.location, check_location)
	dispatcher.add_handler(location_handler)

	updater.start_polling()
	