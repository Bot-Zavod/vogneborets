from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from init import BotInitialize
import logging
from time import sleep
from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def start_command(update, context):
	sticker = "CAADAgAD_iAAAulVBRgi4A0qOPfBBRYE"
	context.bot.sendSticker(chat_id=update.effective_chat.id, sticker=sticker)
	text = "Добрый день!"
	context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)


def help_command(update, context):
	sticker = "CAADAgADCSEAAulVBRjFPBc0MGnDUhYE"
	context.bot.sendSticker(chat_id=update.effective_chat.id, sticker=sticker)
	text = "*Чем могу помочь?*"
	context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)


def unknown(update, context):
	text = "*Я вас не понимаю!(*"
	context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
	

def test_alex(update, context):
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

	start_handler = CommandHandler('start', start_command)
	dispatcher.add_handler(start_handler)

	help_handler = CommandHandler('help', help_command)
	dispatcher.add_handler(help_handler)

	test_alex = CommandHandler('test', test_alex)
	dispatcher.add_handler(test_alex)

	unknown_handler = MessageHandler(Filters.all, unknown)
	dispatcher.add_handler(unknown_handler)


	updater.start_polling()
	