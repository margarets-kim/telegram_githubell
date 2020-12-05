from django.shortcuts import render
import os
import telegram
from telegram.ext import Updater, CommandHandler
from django.http import HttpResponse
import requests

TOKEN="1259085830:AAFNuPKWM4yNnn1xvdNip9ADGZGCMb4sFmk"
url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

bot = telegram.Bot(token=TOKEN)
chat_id = bot.getUpdates()[-1].message.chat.id

custom_keyboard=[['/add','/check']]
reply_markup=telegram.ReplyKeyboardMarkup(custom_keyboard)
#bot.send_message(chat_id=chat_id, text="Custom Keyboard Test", reply_markup=reply_markup)

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

updates = bot.getUpdates()

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="안녕, 나는 깃허브 레포 알람 봇이야~!!", reply_markup=reply_markup)

def repoStatus(update, context):
    res = requests.get(f"http://margarets.pythonanywhere.com/api/alias/?id={update.effective_chat.id}")
    res=json.loads(res.content)
    print(res['alias'])
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"{res['alias']}")

start_handler = CommandHandler('start', start)
repoStatus_handler = CommandHandler('check', repoStatus)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(repoStatus_handler)

updater.start_polling()