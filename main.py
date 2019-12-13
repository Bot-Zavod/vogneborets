from telegram.ext import Updater, CommandHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup
from init import BotInitialize
import logging



def start(update, context):
	location = KeyboardButton(text='Where are you', request_location = True)
	reply_markup = ReplyKeyboardMarkup([[location]])
	context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!", reply_markup=reply_markup)

def helps(update, context):
	context.bot.send_message(chat_id=update.effective_chat.id, text="How can i help you?")



if __name__ == "__main__":
	logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

	# Initialized
	updater, dispatcher = BotInitialize()

	start_handler = CommandHandler('start', start)
	dispatcher.add_handler(start_handler)

	help_handler = CommandHandler('help', helps)
	dispatcher.add_handler(help_handler)

	

	updater.start_polling()