from django.shortcuts import render

import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler


TOKEN="1259085830:AAFNuPKWM4yNnn1xvdNip9ADGZGCMb4sFmk"

bot = telegram.Bot(token=TOKEN)
chat_id = bot.getUpdates()[-1].message.chat.id

custom_keyboard=[['레포추가','레포확인']]
reply_markup=telegram.ReplyKeyboardMarkup(custom_keyboard)
bot.send_message(chat_id=chat_id, text="Custom Keyboard Test", reply_markup=reply_markup)
#bot.sendMessage(chat_id=chat_id, text='[{}]안녕하세요'.format(chat_id))

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

updates = bot.getUpdates() 
for u in updates :
    #print(u.message)
    if u.message.text == "레포확인":
        chat_id = bot.getUpdates()[-1].message.chat.id
        bot.sendMessage(chat_id=chat_id, text='별명을 선택해주세요')

# Create your views here.

