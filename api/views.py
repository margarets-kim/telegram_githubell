from django.shortcuts import render
import os
import telegram
from telegram.ext import Updater, CommandHandler
from django.http import HttpResponse
import requests

TOKEN="1259085830:AAFNuPKWM4yNnn1xvdNip9ADGZGCMb4sFmk"
url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

p=requests.post(url).json()

print(p)

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