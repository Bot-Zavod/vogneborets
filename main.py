from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from GeoReverse import CoordinatesToAdress
from TwinklyDb import *
from init import *
from users import UserManager, User
import logging
import threading
import etc

# LOGSLOGSLOGS
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def start_state(update, context):
	# Create User
    UM.create_user(User(update.message.chat.id,update.message.chat.username))

    # Keyboard generate
    loc_button = KeyboardButton(text=etc.text["check"], request_location = True)
    reply_markup = ReplyKeyboardMarkup([[loc_button], [etc.text["advise"]]], resize_keyboard=True)

    # Message text
    text = etc.text["start_0"] + update.message.chat.first_name + etc.text["start_1"]

    # Sending message
    update.message.reply_sticker(sticker=etc.sticker_twinkly)
    update.message.reply_text(text=text,parse_mode='markdown')
    update.message.reply_text(text=etc.text["send_loc"], reply_markup=reply_markup, parse_mode='markdown')
    logger.info("User %s: send /start command", update.message.chat.id)



def help_state(update, context):
	# Sending a help text
    update.message.reply_text(text=etc.text['help'])
    logger.info("User %s: send /help command", update.message.chat.id)



def usual_state(update, context):
	# Keyboard generate
    loc_button = KeyboardButton(text=etc.text["check"], request_location = True)
    reply_markup = ReplyKeyboardMarkup( [[loc_button], [etc.text["advise"]]], resize_keyboard=True)

    # Sending message
    update.message.reply_text(text=etc.text["usual"], reply_markup=reply_markup, parse_mode='markdown')



def instruction_state(update, context):
	# Sending message
    update.message.reply_text(text=etc.text['safe'])
    logger.info("User %s: ask instructions", update.message.chat.id)



def action_select_state(update, context):
    msg = update.effective_message.text
    place = next(el for el in UM.currentUsers[update.message.chat.id].place if el['name'] == msg)
    UM.currentUsers[update.message.chat.id].selectPlace(place)

    # Keyboard generate
    buttons = [[etc.text['mark']], [etc.text['stat']]]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard = False)

    # Sending message
    update.message.reply_text(text=etc.text['state'], reply_markup=reply_markup)
    logger.info("User %s: select place %s", update.message.chat.id, place)



def location_state(update, context):
    if update.message.chat.id not in UM.currentUsers.keys():
        UM.create_user(User(update.message.chat.id,update.message.chat.username))

    # Generate locations variants
    lat = update.effective_message.location.latitude
    lng = update.effective_message.location.longitude
    UM.currentUsers[update.message.chat.id].addLocation((lat,lng))
    variants = CoordinatesToAdress((lat,lng))

    # Sending message if ZERO RESULTS
    if len(variants) == 0:
    	 update.message.reply_text(text=etc.text['loc_none'], parse_mode='markdown')

    # Save variants for further selection
    UM.currentUsers[update.message.chat.id].selectPlace(variants)

    # USE REGEXP TO HANDLE MESSAGES
    reg = '^'+'|'.join([el['name'] for el in variants])+'$'
    dispatcher.add_handler(MessageHandler(Filters.regex(reg), action_select_state), group=0)

    # Display markup keyboard
    buttons = [[el['name']] for el in variants]
    upd_button =[KeyboardButton(text=etc.text['no_adress'])]
    reply_markup = ReplyKeyboardMarkup([upd_button, *buttons], resize_keyboard=True, one_time_keyboard = True)

    # Sending message
    update.message.reply_text(text=etc.text['clarification'], reply_markup=reply_markup)



def no_adress(update, context):
	# Sending message
    update.message.reply_text(text=etc.text['loc_none'], parse_mode='markdown')
    logger.info("User %s: send no adress", update.message.chat.id)



def mark_text(comments, i, user):
	final = { 0: tc.text["users"], 1: etc.text["users_stat"] }[i]

	avgmark = Review.getMark(user.place['id'])
	message = final+str(avgmark)+"/100\n\n"+etc.text["com"]

	for cmt in comments:
		message = message + cmt + '\n'

	message = message + etc.text["link"]
	logger.info("User %s: send no adress", update.message.chat.id)
	return message



def loc_info_state(update, context):
    user = UM.currentUsers[update.message.chat.id]
    comments = Review.getComments(user.place['id'], user.chat_id)
    logger.info("User %s: ask place marks", update.message.chat.id)
    
    # Sending message
    if len(comments) > 0:
        message = mark_text(comments, 1, user)
        context.bot.send_message(update.message.chat.id, text=message, parse_mode='markdown')
    else:
        context.bot.send_message(update.message.chat.id, text=etc.text['no_review'], parse_mode='markdown')



def loc_save_state(update, context):
    place = UM.currentUsers[update.message.chat.id].place
    questions = etc.all_types[place['typ']].copy()
    UM.currentUsers[update.message.chat.id].addQuestions(questions)

    # Delete reply keyboard with start buttons
    text = etc.text['test_start']
    context.bot.send_message(update.message.chat.id, text=text, parse_mode='markdown', reply_markup=ReplyKeyboardRemove())
    logger.info("User %s: start place estimate", update.message.chat.id)

    ask_question(update, context)



def ask_question(update, context):
    if update.callback_query:
        update = update.callback_query
    user = UM.currentUsers[update.message.chat.id]

    button_y = InlineKeyboardButton(etc.text["yes"], callback_data='yes')
    button_n = InlineKeyboardButton(etc.text["no"], callback_data='no')
    button_idn = InlineKeyboardButton(etc.text["dk"], callback_data='idn')
    button_info = InlineKeyboardButton(etc.text["info"], callback_data='info')
    keyboard = InlineKeyboardMarkup([[button_y, button_n],[button_idn,button_info]])

    update.message.reply_text(text=etc.question[user.questions[0]], parse_mode='markdown', reply_markup=keyboard)


# Sending questions and comment request message
def user_answer(update, context):
    query = update.callback_query
    query.answer()

    answer = 0 if query.data == 'no' else 1 if query.data == 'yes' else 0
    remaining_questions = UM.currentUsers[query.message.chat.id].questions
    question = remaining_questions.pop(0)
    UM.currentUsers[query.message.chat.id].addAnswer(question,answer)
    context.bot.delete_message(query.message.chat.id, query.message.message_id) 

    # Send COMMENT TEXT to listen comments
    if len(remaining_questions) > 0:
        ask_question(update, context)
    else:
        dispatcher.add_handler(MessageHandler(Filters.text, submit_review), group=1)
        text = etc.text['comment']
        reply_markup = ReplyKeyboardMarkup([[etc.text["cancel_comment"]]], resize_keyboard=True, one_time_keyboard = True)
        context.bot.send_message(query.message.chat.id, text=text, parse_mode='markdown', reply_markup=reply_markup)
    

def user_info(update, context):
    query = update.callback_query
    q = UM.currentUsers[query.message.chat.id].questions[0]

    if q in etc.images.keys():
        context.bot.send_photo(chat_id=query.message.chat.id, photo=open(etc.images[q], 'rb'))
    context.bot.send_message(query.message.chat.id, text=etc.info[q])
    query.answer()



def submit_review(update, context):
    user = UM.currentUsers[update.message.chat.id]
    comment = '' if update.message.text == etc.text["cancel_comment"] else pdate.message.text
    questions = etc.all_types[user.place['typ']]
    real_answers=[]

    for q in questions:
        if user.answers[q] == etc.right_answers[q]:
            real_answers.append(1)
        else:
            real_answers.append(0)

    # Write REVIEW to DataBase
    mark = 100 * sum(real_answers) // len(real_answers)
    Review.addReview(user.chat_id, json.dumps(user.answers), user.place['typ'], *user.location, user.place['id'], user.place['name'], comment, mark)

    # print submission success & display recent comments
    context.bot.send_message(update.message.chat.id, text=etc.text["submit"]+str(mark)+'/100', parse_mode='markdown', reply_markup=ReplyKeyboardRemove())
    comments = Review.getComments(user.place['id'], user.chat_id)

    if len(comments) > 0:
        message = mark_text(comments,0,user)
        context.bot.send_message(update.message.chat.id, text=message, parse_mode='markdown', reply_markup=ReplyKeyboardRemove())

    UM.delete_user(user.chat_id)
    usual_state(update, context)







if __name__ == "__main__":
    # Initialized BOT
    UM = UserManager()
    updater = Updater(token = bot_token, use_context=True)
    dispatcher = updater.dispatcher

    # Commands
    dispatcher.add_handler(CommandHandler('start', start_state))

    # help command
    dispatcher.add_handler(CommandHandler('help', help_state))

    # Location handler
    dispatcher.add_handler(MessageHandler(Filters.location, location_state))

    # Messages
    dispatcher.add_handler(MessageHandler(Filters.regex(etc.text["advise"]), instruction_state))
    dispatcher.add_handler(MessageHandler(Filters.regex(etc.text["no_adress"]), no_adress))

    # Callback Queries
    dispatcher.add_handler(CallbackQueryHandler(user_answer, pattern='^(yes|no|idn)$'))
    dispatcher.add_handler(CallbackQueryHandler(user_info, pattern='^(info)$'))

    # REGex   
    dispatcher.add_handler(MessageHandler(Filters.regex(etc.text['mark']), loc_save_state))    	
    dispatcher.add_handler(MessageHandler(Filters.regex(etc.text['stat']), loc_info_state))

    updater.start_polling()
    updater.idle()