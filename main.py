from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from GeoReverse import CoordinatesToAdress
from TwinklyDb import *
from init import bot_token
from users import UserManager, User
import threading
import etc

def start_state(update, context):
    print('START SAVE')
    UM.create_user(User(update.message.chat.id,update.message.chat.username))
    print(UM.currentUsers)
    loc_button = KeyboardButton(text=etc.text["check"], request_location = True)
    buttons = [[loc_button], [etc.text["advise"]]]
    reply_markup = ReplyKeyboardMarkup([*buttons], resize_keyboard=True)
    update.message.reply_sticker(sticker=etc.sticker_twinkly)
    txt = etc.text["start_0"] + update.message.chat.first_name + etc.text["start_1"]
    update.message.reply_text(text=txt,parse_mode='markdown')
    update.message.reply_text(text=etc.text["send_loc"], reply_markup=reply_markup, parse_mode='markdown')

def help_state(update, context):
    update.message.reply_text(text=etc.text['help'])

def usual_state(update, context):
    loc_button = KeyboardButton(text=etc.text["check"], request_location = True)
    buttons = [[loc_button], [etc.text["advise"]]]
    reply_markup = ReplyKeyboardMarkup([*buttons], resize_keyboard=True)
    update.message.reply_text(text=etc.text["usual"], reply_markup=reply_markup, parse_mode='markdown')

def instruction_state(update, context):
    update.message.reply_text(text=etc.text['safe'])

def action_select_state(update, context):
    print('ACTION SELECT')
    msg = update.effective_message.text
    print('got ', msg)
    place = next(el for el in UM.currentUsers[update.message.chat.id].place if el['name'] == msg)
    UM.currentUsers[update.message.chat.id].selectPlace(place)
    buttons = [[etc.text['mark']], [etc.text['stat']]]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard = False)
    update.message.reply_text(text=etc.text['state'], reply_markup=reply_markup)

def location_state(update, context):
    print('LOC STATE')
    if update.message.chat.id not in UM.currentUsers.keys():
        UM.create_user(User(update.message.chat.id,update.message.chat.username))
    lat = update.effective_message.location.latitude
    lng = update.effective_message.location.longitude
    UM.currentUsers[update.message.chat.id].addLocation((lat,lng))
    variants = CoordinatesToAdress((lat,lng))
    print(lat,lng)
    print(len(variants))
    # Save variants for further selection
    UM.currentUsers[update.message.chat.id].selectPlace(variants)
    # USE REGEXP TO HANDLE MESSAGES
    reg = '^'+'|'.join([el['name'] for el in variants])+'$'
    dispatcher.add_handler(MessageHandler(Filters.regex(reg), action_select_state), group=0)
    # Display markup keyboard
    buttons = [[el['name']] for el in variants]
    upd_button =[KeyboardButton(text=etc.text['no_adress'])]
    reply_markup = ReplyKeyboardMarkup([upd_button, *buttons], resize_keyboard=True, one_time_keyboard = True)
    update.message.reply_text(text=etc.text['clarification'], reply_markup=reply_markup)

def no_adress(update, context):
    update.message.reply_text(text=etc.text['loc_none'],parse_mode='markdown')

def mark_text(comments,i,user):
    if i == 0:
        final = etc.text["users"]
    else:
        final = etc.text["users_stat"]
    avgmark = Review.getMark(user.place['id'])
    message = final+str(avgmark)+"/100\n\n"+etc.text["com"]
    for cmt in comments:
        message = message + cmt + '\n'
    message = message + etc.text["link"]
    return message

def loc_info_state(update, context):
    print('[INFO]')
    user = UM.currentUsers[update.message.chat.id]
    print(user)
    print(user.place)
    comments = Review.getComments(user.place['id'], user.chat_id)
    if len(comments) > 0:
        message = mark_text(comments,1,user)
        context.bot.send_message(update.message.chat.id, text=message, parse_mode='markdown')
    else:
        context.bot.send_message(update.message.chat.id, text=etc.text['no_review'], parse_mode='markdown')

def loc_save_state(update, context):
    print('LOC SAVE')
    print('Review start')
    place = UM.currentUsers[update.message.chat.id].place
    print('place', place)
    questions = etc.all_types[place['typ']].copy()
    print('typ', place['typ'])
    UM.currentUsers[update.message.chat.id].addQuestions(questions)
    print('etc', etc.all_types[place['typ']])
    print('questions', questions)
    print('saving', place)
    ask_question(update, context)

def ask_question(update, context):
    print('ASK_Q')
    if update.callback_query:
        update = update.callback_query
    user = UM.currentUsers[update.message.chat.id]
    print(user.questions)
    button_y = InlineKeyboardButton(etc.text["yes"], callback_data='yes')
    button_n = InlineKeyboardButton(etc.text["no"], callback_data='no')
    button_idn = InlineKeyboardButton(etc.text["dk"], callback_data='idn')
    button_info = InlineKeyboardButton(etc.text["info"], callback_data='info')
    keyboard = InlineKeyboardMarkup([[button_y, button_n],[button_idn,button_info]])
    update.message.reply_text(text=etc.question[user.questions[0]], parse_mode='markdown', reply_markup=keyboard)

def user_answer(update, context):
    print('USER_ANSWER')
    query = update.callback_query
    query.answer()
    answer = 0 if query.data == 'no' else 1 if query.data == 'yes' else 0
    remaining_questions = UM.currentUsers[query.message.chat.id].questions
    question = remaining_questions.pop(0)
    print('answered ', question, answer)
    UM.currentUsers[query.message.chat.id].addAnswer(question,answer)
    if len(remaining_questions) > 0:
        ask_question(update, context)
    else:
        dispatcher.add_handler(MessageHandler(Filters.text, submit_review), group=1)
        text = etc.text['comment']
        context.bot.send_message(query.message.chat.id, text=text, parse_mode='markdown', reply_markup=ReplyKeyboardRemove())
    context.bot.delete_message(query.message.chat.id, query.message.message_id) 

def user_info(update, context):
    query = update.callback_query
    q = UM.currentUsers[query.message.chat.id].questions[0]
    if q in etc.images.keys():
        context.bot.send_photo(chat_id=query.message.chat.id, photo=open(etc.images[q], 'rb'))
    context.bot.send_message(query.message.chat.id, text=etc.info[q])
    query.answer()

def submit_review(update, context):
    print('review submission')
    user = UM.currentUsers[update.message.chat.id]
    comment = update.message.text
    questions = etc.all_types[user.place['typ']]
    real_answers=[]
    for q in questions:
        if user.answers[q] == etc.right_answers[q]:
            real_answers.append(1)
        else:
            real_answers.append(0)
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
    updater = Updater(token=bot_token, use_context=True)
    dispatcher = updater.dispatcher

    ### Handlers

    # Commands
    dispatcher.add_handler(CommandHandler('start', start_state))
    dispatcher.add_handler(CommandHandler('help', help_state))
    # Location
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