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

custom_keyboard=[['레포추가','레포확인']]
reply_markup=telegram.ReplyKeyboardMarkup(custom_keyboard)
#bot.send_message(chat_id=chat_id, text="Custom Keyboard Test", reply_markup=reply_markup)

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

updates = bot.getUpdates()

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

def repoStatus(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='your repo list')

start_handler = CommandHandler('start', start)
repoStatus_handler = CommandHandler('repo', repoStatus)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(repoStatus_handler)

updater.start_polling()

""" p=requests.post(url).json()
print(p) """

""" PORT = int(os.environ.get('PORT','8443'))
updater = Updater(TOKEN, use_context=True)

dispatcher = updater.dispatcher

dispatcher.add_hadler((CommandHandler("start",start)))

updater.start_webhook(  
                        listen="0.0.0.0",
                        port=PORT,
                        url_path=TOKEN
                                        )

updater.bot.set_webhook("https://alarm-bot-repo.herokuapp.com/"+TOKEN)
updater.idle()

def start(bot, update):
    update.message.reply_text('Hi! I'm repoBot')  """