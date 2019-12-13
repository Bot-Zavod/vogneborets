from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from init import BotInitialize
import logging
from time import sleep
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def start_command(update, context):
	sticker = "CAADAgAD_iAAAulVBRgi4A0qOPfBBRYE"
	context.bot.sendSticker(chat_id=update.effective_chat.id, sticker=sticker)
	text = "Привет, Михалыч епта!"
	context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
	button1 = InlineKeyboardButton('кнопка1', callback_data='1')
	button2 = InlineKeyboardButton('кнопка2', callback_data='2')
	keyboard = InlineKeyboardMarkup([[button1, button2],[button1, button2]])

	context.bot.sendMessage(chat_id=update.effective_chat.id, text='fuck', reply_markup=keyboard)

def help_command(update, context):
	sticker = "CAADAgADCSEAAulVBRjFPBc0MGnDUhYE"
	context.bot.sendSticker(chat_id=update.effective_chat.id, sticker=sticker)
	text = "Че надо блять?"
	context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)

def unknown(update, context):
	text = "Че ты пиздишь? Я не понимаю нахуй!"
	context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)
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

	unknown_handler = MessageHandler(Filters.all, unknown)
	dispatcher.add_handler(unknown_handler)


	updater.start_polling()
	