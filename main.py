from telegram.ext import Updater, CommandHandler
import logging

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

def helper(update, context):
	context.bot.send_message(chat_id=update.effective_chat.id, text="How can i help you?")

if __name__ == "__main__":
	logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

	# Initialised
	updater = Updater(token='850462457:AAHRS7lOavs3VgD7_PR-QqcXXSkhnYT8Kho', use_context=True)
	dispatcher = updater.dispatcher

	start_handler = CommandHandler('start', start)
	dispatcher.add_handler(start_handler)

	help_handler = CommandHandler('help', helper)
	dispatcher.add_handler(help_handler)

	updater.start_polling()
