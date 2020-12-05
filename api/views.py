from django.shortcuts import render
import os
import telegram
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from django.http import HttpResponse
import requests, json

TOKEN="1259085830:AAFNuPKWM4yNnn1xvdNip9ADGZGCMb4sFmk"
url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

bot = telegram.Bot(token=TOKEN)
#chat_id = bot.getUpdates()[-1].message.chat.id

custom_keyboard=[['/add','/check']]
reply_markup=telegram.ReplyKeyboardMarkup(custom_keyboard)
#bot.send_message(chat_id=chat_id, text="Custom Keyboard Test", reply_markup=reply_markup)

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

updates = bot.getUpdates()

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="안녕, 나는 깃허브 레포 알람 봇이야~!!", reply_markup=reply_markup)

def repoStatus(update, context):
    repoList = []
    res = requests.get(f"http://margarets.pythonanywhere.com/api/alias/?id={update.effective_chat.id}")
    res=json.loads(res.content)
    print(res['alias'])
    resLength = len(res['alias'])

    for i in range(0,resLength):
        repoList.append([InlineKeyboardButton(text=f"{res['alias'][i]}", callback_data=f"{res['alias'][i]}")])

    repoMarkup = InlineKeyboardMarkup(repoList)
    update.message.reply_text("원하는 레포별명을 선택해주세요", reply_markup=repoMarkup)

def changeKST(ISO):
    yyyymmdd, time = ISO.split('T')
    yyyy, mm, dd = yyyymmdd.split('-')
    hour, minute, second = time.split(':')
    second,Z = second.split('Z')
    hour=int(hour)+9
    if hour>=24:
        hour-=24
    hour=str(hour)
    #KST = yyyy + "년" + mm + "월" + dd + "일 " + hour + "시" + minute + "분" + second + "초"
    KST = yyyymmdd + " " + hour + ":" + minute + ":" + second
    return KST

def callbackGet(update, context):
    data = {'id':f'{update.effective_chat.id}','nick_name':f'{update.callback_query.data}'}
    res = requests.get("http://margarets.pythonanywhere.com/api/git/",params=data)
    res = json.loads(res.content)
    repoURL = res['repoUrl']
    repoBRANCH = res['repoBranch']
    data2 = { 'id' : f'{update.effective_chat.id}', 'nick_name' : f'{update.callback_query.data}', 'fav_repository' : f'{repoURL}', 'type' : 'telegram', 'branch' : f'{repoBRANCH}'}
    res2 = requests.get("http://margarets.pythonanywhere.com/api/", params = data2)
    res2 = json.loads(res2.content)
    
    if res2 == []:
        return_res2 = "해당 레포 업데이트 사항이 없습니다."
    elif res2 == None:
        return_res2 = "해당 레포 업데이트 사항이 없습니다."
    else:
        ISO = res2[0].get("commit").get("committer").get("date")
        KST = changeKST(ISO)
        return_res2 = f"[{update.callback_query.data}] 최근 커밋 이력입니다.\n"
        return_res2 = return_res2 + "날짜 : " + KST + "\n"
        return_res2 = return_res2 + "이름 : " + res2[0].get("commit").get("committer").get("name") + "\n"
        return_res2 = return_res2 + "이메일 : " + res2[0].get("commit").get("committer").get("email") + "\n"
        return_res2 = return_res2 + "커밋메세지 : " + res2[0].get("commit").get("message") + "\n"
        return_res2 = return_res2 + "주소 : " + res2[0].get("html_url")

    context.bot.edit_message_text(text=f"{return_res2}",
                                  chat_id=update.callback_query.message.chat_id,
                                  message_id=update.callback_query.message.message_id)

start_handler = CommandHandler('start', start)
repoStatus_handler = CommandHandler('check', repoStatus)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(repoStatus_handler)
dispatcher.add_handler(CallbackQueryHandler(callbackGet))

updater.start_polling()