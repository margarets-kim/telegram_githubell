from django.shortcuts import render
import os
import telegram
from telegram.ext import Updater, CommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from django.http import HttpResponse
import requests, json

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

def buildMenu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i+n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

def repoStatus(update, context):
    repoList = []
    res = requests.get(f"http://margarets.pythonanywhere.com/api/alias/?id={update.effective_chat.id}")
    res=json.loads(res.content)
    print(res['alias'])


    for i in len(res['alias']):
        repoList.append(InlineKeyboardButton(f"{res['alias'][i]}", callback_data=f"{res['alias'][i]}"))

    repoMarkup = InlineKeyboardMarkup(buildMenu(repoList, len(repoList)-1))
    update.message.reply_text("원하는 레포별명을 선택해주세요", reply_markup=repoMarkup)

def callbackGet(update, context):
    data = {'id':f'{update.effective_chat.id}','nick_name':f'{update.callback_query.data}'}
    res = requests.get("http://margarets.pythonanywhere.com/api/git/",params=data)
    res = json.loads()
    print(res)
    repoURL = res['repoUrl']
    repoBRANCH = res['repoBranch']
    data2 = { 'id' : f'{update.effective_chat.id}', 'nick_name' : f'{update.callback_query.data}', 'fav_repository' : f'{repoURL}', 'type' : 'telegram', 'branch' : f'{repoBRANCH}'}
    res2 = requests.get("http://margarets.pythonanywhere.com/api/", data = data2)
    res2 = json.loads()
    context.bot.edit_message_text(text=f"{res2}")

start_handler = CommandHandler('start', start)
repoStatus_handler = CommandHandler('check', repoStatus)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(repoStatus_handler)

updater.start_polling()