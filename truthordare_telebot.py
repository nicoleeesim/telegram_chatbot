from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
from telegram.ext import RegexHandler
from telegram.callbackquery import CallbackQuery
from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update
from telegram.message import Message
import sys
import pandas as pd
import telebot
from telebot import types

import random

token = '1132171705:AAHJ_FeVySggyC0DwGmfQhwkbNTsd8joxFY' #fill up with your token

tele_bot = telebot.TeleBot(token) # using telebot wrapper
tele_bot_updates = tele_bot.get_updates()
chat_id = tele_bot_updates[-1].message.chat.id

#importing truthdare qns files
truth_df = pd.read_csv('truth.csv')
dare_df = pd.read_csv('dare.csv')

# for conversational handler
FIRST, SECOND, THIRD = range(3)

# select a random name
def randomizer(action, names="Derek, Pearlyn, Ben, Nicole, Claire"):
    f = open("names.txt", "r")
    contents = f.read()
    if len(contents) == 0: #use default if there is no names
        lst = ['Derek', 'Pearlyn', 'Ben', 'Nicole', 'Claire']
        return lst[random.randint(0,len(lst))]
    elif action =='add': #add names
        f = open("names.txt", "w+")
        f.write(names)
        f.close
        f = open("names.txt", "w+")
        contents = f.read()
        name_list = contents.split(",")
        return name_list[random.randint(0,len(name_list))]
    elif action == 'select': #added names, now select
        name_list = contents.split(",")
        return name_list[random.randint(0,len(name_list))]

# creating updater
updater: Updater = Updater(token,use_context=True)

# on /start command
def start(update: Update, context: CallbackContext):
    bot: Bot = context.bot 
    
    # creating keyboard options
    keyboard = [[
        InlineKeyboardButton("Enter Names", callback_data='add_names'),
        InlineKeyboardButton("Spin the Bottle", callback_data='select_name')
    ]] 

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Welcome to a game of Truth or Dare! \n Please choose:', reply_markup=reply_markup)
 
    return FIRST

def first(update, context):
    """
    callback method handling button press
    """
    # getting the callback query
    query: CallbackQuery = update.callback_query
    query.answer()

    if query.data == "select_name":
        selected_name = randomizer(action='select')
        td_keyboard = [[
        InlineKeyboardButton("Truth", callback_data='truth'),  
        InlineKeyboardButton("Dare", callback_data='dare')
    ]]
        td_reply_markup = InlineKeyboardMarkup(td_keyboard)
        query.message.reply_text("Lucky one: " + selected_name + '!\nPlease choose:', reply_markup=td_reply_markup)
        return SECOND
    
    elif query.data == "add_names":
        tele_bot.send_message(chat_id, "Please enter pplayers' names (eg, Lisa, Mary, Ben):")
        return THIRD

def second(update, context):
    query: CallbackQuery = update.callback_query
    query.answer()
    if query.data == "truth":
        qns = truth_df.iloc[random.randint(0,98)].values[0]
        query.message.reply_text(text=qns)
    else:
        qns = dare_df.iloc[random.randint(0,98)].values[0]
        query.message.reply_text(text=qns)
    pass

def third(update, context): 
    # Next implementation. Issues with getting user's response. 
    # Tried these but failed: (1) register_next_step_handler - doesnt send message out (2) callbackquery - only works for buttons
    pass 

# adding listeners. using states to manage multiple callbackqueries
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        FIRST: [CallbackQueryHandler(first)],
        SECOND: [CallbackQueryHandler(second)]
    },
    fallbacks=[CommandHandler('start', start)]
)

updater.dispatcher.add_handler(conv_handler)

# start polling updates from telegram
updater.start_polling()


