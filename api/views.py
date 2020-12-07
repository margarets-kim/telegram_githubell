import logging
from django.shortcuts import render
import telegram
from rest_framework.views import APIView
from rest_framework.response import Response
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import Updater, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
#from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from django.http import HttpResponse
import requests
import json
from urllib.request import urlopen
import re
from . import getGithub

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
p = re.compile('\$branch_*(.*)')
a = re.compile('\$Alias_*(.*)')
c = re.compile('\$Check_*(.*)')

BRANCH, ALIAS, TYPING, SEND, CHECK, STATUS, HOW = range(7)

TOKEN = "1498546920:AAFFE6PJlfZjFvWS51fvwDElA0ay6k96QEI"
bot = telegram.Bot(token=TOKEN)


class UserAlarm (APIView):

    def get(self, request):
        try:
            chat_id = request.GET.get('id', '')
            nick_name = request.GET.get('nick_name', '')
            committer = request.GET.get('name', '')
            email = request.GET.get('email', '')
            msg = request.GET.get('msg', '')
            url = request.GET.get('url', '')
            ISO = request.GET.get('date', '')

            KST = changeKST(ISO)

            return_res = f"[{nick_name}] 커밋이력입니다.\n"
            return_res = return_res + f"날짜 : {KST}\n"
            return_res = return_res + f"이름 : {committer}\n"
            return_res = return_res + f"이메일 : {email}\n"
            return_res = return_res + f"커밋메세지 : {msg}\n"
            return_res = return_res + f"주소 : {url}"

            bot.send_message(chat_id=chat_id, text=f"{return_res}")

            return Response(status=200)

        except Exception as e:
            return Response("error", status=404)


custom_keyboard = [['/howto', '/check', '/start']]
reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)


def start(update: Update, context: CallbackContext) -> None:  # 시작할 때 호출되는 함수]
    update.message.reply_text("안녕!, 난 깃허벨이야 :D", reply_markup=reply_markup)

    try:
        user = update.message.from_user
        id = context.args[0]
        data = getGithub.urlGet(id)
        update.message.reply_text(data['name'] + ' 레포지토리를 등록하려고하는구나!')
        context.user_data[0] = user.id
        context.user_data[1] = data['name']
        update.message.reply_text('등록을 위해 몇가지 절차가 필요해!')
        branchList = []
        for i in data['branch_lists']:
            branchList.append([InlineKeyboardButton(
                text=f"{i}", callback_data=f"$branch_"+i)])
        brMarkup = InlineKeyboardMarkup(branchList)

        update.message.reply_text(
            '먼저 브랜치를 골라줘!', reply_markup=brMarkup)
        # update.message.reply_text("먼저 브랜치를 골라줄래?", reply_markup=brMarkup)
        return BRANCH

    except(IndexError, ValueError):
        update.message.reply_text(
            'https://githubell.netlify.app/ 에서 깃허브 레포지토리를 등록할수있어!')

# 브랜치 선택에 대한 대답 (BRANCH)


def branch(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = p.match(query.data).group(1)
    query.answer()
    bot.send_message(chat_id=query.message.chat_id, text=f'{data} 브랜치를 골랐구나?')
    context.user_data[2] = data
    print(context.user_data)
    text = "이제 별명을 입력해줘!"
    bot.send_message(chat_id=query.message.chat_id, text=text)
    bot.send_message(chat_id=query.message.chat_id,
                     text='/skip 을 치면 별명 설정은 생략될거야!')

    return TYPING


def skip_alias(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    logger.info("%s은 별명입력을 하지 않음", user.first_name)
    bot.send_message(chat_id=query.message.chat_id,
                     text=f'알겠어! 기본 레포지토리 이름인 {context.user_data[1]}으로 등록해둘게!')
    context.user_data[3] = data['name']
    callback_data = str(SEND)
    return SEND


def saveAlias(update: Update, context: CallbackContext):
    query = update.callback_query
    context.user_data[3] = update.message.text
    bot.send_message(chat_id=update.message.chat.id,
                     text=f'{context.user_data[3]} 라는 별명으로 등록해둘게!')
    keyboard = [
        [
            InlineKeyboardButton("데이터 보내기", callback_data='SEND'),
            InlineKeyboardButton("취소", callback_data='END'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(chat_id=update.message.chat.id,
                     text="이제 데이터 보내기를 눌러서 최종적으로 등록해줘!", reply_markup=reply_markup
                     )
    # user_data[START_OVER] = True
    return SEND


def send(update: Update, context: CallbackContext) -> None:

    query = update.callback_query
    query.answer()
    bot.send_message(chat_id=query.message.chat.id,
                     text=f'{context.user_data[3]} 레포지토리가 성공적으로 등록됐어! 이제 새로운 업데이트가 생기면 내가 알려줄게!')
    print(context.user_data)
    return ConversationHandler.END


def repoStatus(update, context):  # 레포리스트를 가져와서 고르는 함수
    repoList = []
    res = requests.get(
        f"http://margarets.pythonanywhere.com/api/alias/?id={update.effective_chat.id}")
    res = json.loads(res.content)
    resLength = len(res['alias'])

    for i in range(0, resLength):
        repoList.append([InlineKeyboardButton(
            text=f"{res['alias'][i]}", callback_data=f"$Check_"+{res['alias'][i]})])

    repoMarkup = InlineKeyboardMarkup(repoList)
    update.message.reply_text("원하는 레포별명을 선택해주세요", reply_markup=repoMarkup)
    return STATUS


def end(update: Update, context: CallbackContext) -> None:
    bot.send_message(chat_id=update.message.chat.id,
                     text='레포지토리 등록이 중단되었어:(')
    return ConversationHandler.END


def changeKST(ISO):  # ISO -> KST 시간 변환
    yyyymmdd, time = ISO.split('T')
    yyyy, mm, dd = yyyymmdd.split('-')
    hour, minute, second = time.split(':')
    second, Z = second.split('Z')
    hour = int(hour)+9
    if hour >= 24:
        hour -= 24
    hour = str(hour)
    # KST = yyyy + "년" + mm + "월" + dd + "일 " + hour + "시" + minute + "분" + second + "초"
    KST = yyyymmdd + " " + hour + ":" + minute + ":" + second
    return KST


def callbackGet(update, context):  # 레포 선택에 대한 대답
    data = {'id': f'{update.effective_chat.id}',
            'nick_name': f'{c.match(update.callback_query.data).group(1)}'}
    res = requests.get(
        "http://margarets.pythonanywhere.com/api/git/", params=data)
    res = json.loads(res.content)
    repoURL = res['repoUrl']
    repoBRANCH = res['repoBranch']
    data2 = {'id': f'{update.effective_chat.id}', 'nick_name': f'{update.callback_query.data}',
             'fav_repository': f'{repoURL}', 'type': 'telegram', 'branch': f'{repoBRANCH}'}
    res2 = requests.get(
        "http://margarets.pythonanywhere.com/api/", params=data2)
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
        return_res2 = return_res2 + "이름 : " + \
            res2[0].get("commit").get("committer").get("name") + "\n"
        return_res2 = return_res2 + "이메일 : " + \
            res2[0].get("commit").get("committer").get("email") + "\n"
        return_res2 = return_res2 + "커밋메세지 : " + \
            res2[0].get("commit").get("message") + "\n"
        return_res2 = return_res2 + "주소 : " + res2[0].get("html_url")

    context.bot.edit_message_text(text=f"{return_res2}",
                                  chat_id=update.callback_query.message.chat_id,
                                  message_id=update.callback_query.message.message_id)
    return ConversationHandler.END


def howto(update, context):
    bot.send_message(chat_id=update.message.chat.id,
                     text='관심있거나 소식받고싶은 레포지토리가 있니?')
    bot.send_message(chat_id=update.message.chat.id,
                     text='https://githubell.netlify.app/ 에서 깃허브 레포지토리를 등록할수있어!')
    bot.send_message(chat_id=update.message.chat.id,
                     text='깃허벨 홈페이지에서 만든 큐알코드를 인식 어플로 인식시켜주면 내가 기억해둘게!')
    return ConversationHandler.END
# start_handler = CommandHandler('start', start, pass_args=True)
# repoStatus_handler = CommandHandler('check', repoStatus)

# dispatcher.add_handler(start_handler)
# dispatcher.add_handler(repoStatus_handler)


'''dispatcher.add_handler(CallbackQueryHandler(
    callbackBranchGet, pattern=p))
dispatcher.add_handler(CallbackQueryHandler(
    callbackAliasGet, pattern=a))
# dispatcher.add_handler(MessageHandler(Filters.text, GetAlias))'''

# url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
# bot = telegram.Bot(token=TOKEN)
print('start main')
updater = Updater(token=TOKEN, use_context=True)

dispatcher = updater.dispatcher

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        BRANCH: [CallbackQueryHandler(branch, pattern=p)],
        ALIAS: [CallbackQueryHandler(saveAlias, pattern='^(?!\/skip).*$'), CommandHandler('skip', skip_alias)],
        TYPING: [MessageHandler(Filters.text & ~Filters.command, saveAlias)],
        SEND: [CallbackQueryHandler(send, pattern='^SEND$')],
        CHECK: [CommandHandler('check', repoStatus)],
        STATUS: [(CallbackQueryHandler(callbackGet, pattern=c))],
        HOW: [CommandHandler('howto', howto)],
    },
    fallbacks=[CallbackQueryHandler(end, pattern='^END$')]
)
dispatcher.add_handler(conv_handler)
# dispatcher.add_handler(CallbackQueryHandler(callbackGet, pattern=c))

updater.start_polling(timeout=5, poll_interval=1, clean=True)
