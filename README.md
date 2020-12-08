# telegram_githubell

Githubell 파이썬 기반 텔레그램 봇입니다!

## 실행 스크립트

### Step 1. 가상환경 생성하기

### `python -m venv {가상환경 이름}`

해당 명령어를 통해 현재 위치한 경로에 파이썬 가상환경을 생성할 수 있습니다\
해당 프로젝트의 파이썬 버전은 3.8입니다!

### mac/Linux 가상 환경 실행 명령어

### `source {가상환경이름}/bin/activate {가상환경이름}`

### window 가상 환경 실행 명령어

### `source {가상환경이름}/Script/activate {가상환경이름}`

### 가상 환경 종료 명령어

### `deactivate`

### Step 2. pip install

### `pip install -r requirments.txt`

가상환경을 실행한 후 해당 명령어를 통해 패키지 파일을 모두 설치하세요

### Step 3. 서버 실행하기

### `python manage.py runserver`

해당 명령어를 실행시키면 텔레그램 봇이 실행됩니다 :)\
아직 Bot token을 입력하지 않았으므로 실행하진 마세요!

### Step 4. Bot 토큰 넣기

api 폴더 속에 env.py 파일을 생성하고 아래와 같이 작성하세요!

```
./api/env.py

def token():
    value = {Bot 토큰}
    return value
```

해당 파일을 만들고 서버를 실행해야 텔레그램 봇이 실행됩니다 :)\

## Telegram Bot

카카오톡의 '선톡'기능 사용 불가 이슈로 추가된 메신저 플랫폼입니다. \카카오톡 봇에 비해 큰 제약없이 챗봇을 사용할 수 있으며 무료로 사용할 수 있습니다

## HOST SERVER - PythonAnywhere

PythonAnywhere는 Django를 운영하는데 가장 효율적으로 서비스를 제공하여 줍니다.
몇번의 조작으로 서버 구성을 해줄 뿐 아니라 여러가지 방면에서 개발자를 위한 편리한 서비스를 제공하여 줍니다

## 소스코드 TREE

```
.
├── Procfile
├── README.md
├── Telegram #저희 메인 앱 이름입니다 :D
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-39.pyc
│   │   ├── settings.cpython-39.pyc
│   │   ├── urls.cpython-39.pyc
│   │   └── wsgi.cpython-39.pyc
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── api #여기서 저희 봇이 동작해요~!
│   ├── __init__.py
│   ├── __pycache__
│   ├── admin.py
│   ├── apps.py
│   ├── getGithub.py #깃허브에서 정보를 가져옵니다
│   ├── migrations
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py #해당 파일에서 봇이 동작함!
├── db.sqlite3
├── manage.py #메인 실행 파일
├── myvenv #가상환경을 저장하는 폴더
├── requirements.txt #패키지 통합 설치 파일
├── runtime.txt
├── static
│   └── no
└── staticfiles
```

# BACK-END API

이 API는 POST 및 GET 요청을 사용 하여 통신하고 HTTP 응답 코드 를 사용 하여 상태 및 오류를 표시합니다. 모든 응답은 표준 JSON으로 제공됩니다.
모든 요청에는 content-typeof 가 포함됩니다 application/json 되어야하며 본문은 유효한 JSON이어야합니다.

## Bot 실행 코드

```
./api/views.py
import logging
from django.shortcuts import render
import telegram
from rest_framework.views import APIView
from rest_framework.response import Response
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import Updater, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
# from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from django.http import HttpResponse
import requests
import json
from urllib.request import urlopen
import re
from . import getGithub
from . import env

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
p = re.compile('\$branch_*(.*)')
a = re.compile('\$Alias_*(.*)')
c = re.compile('\$Check_*(.*)')

BRANCH, ALIAS, TYPING, SEND, STATUS, CHOOSE = range(6)
TOKEN = env.token()
bot = telegram.Bot(token=TOKEN)


class UserAlarm (APIView):
    def get(self, request):
        try:
           print('bot on')
           #nothing to do...
        except Exception as e:
            return e

#핵심코드
custom_keyboard = [['사용방법'], ['레포지토리 상태 확인'], ['작별인사']]
reply_markup = telegram.ReplyKeyboardMarkup(
    custom_keyboard, one_time_keyboard=False)


def start(update: Update, context: CallbackContext) -> None:  # 시작할 때 호출되는 함수]
    update.message.reply_text("안녕!, 난 깃허벨이야 :D", reply_markup=reply_markup)

    try:
        user = update.message.from_user
        id = context.args[0]
        update.message.reply_text('앗! 새로운 레포지토리를 등록하려고하는구나?')
        owner, repo = getGithub.urlGet(id)
        data = getGithub.bracnhGet(owner, repo)
        update.message.reply_text(data['name'] + ' 레포지토리 맞지?')
        context.user_data[0] = user.id  # 텔레그램 채팅 아이디
        context.user_data[1] = data['name']  # 레포지토리 이름
        # 2번은 선택한 브랜치
        context.user_data[3] = data['name']  # 레포지토리 별명
        # 레포지토리 주소
        context.user_data[4] = f'https://github.com/{owner}/{repo}'
        update.message.reply_text('등록을 위해 몇가지 절차가 필요해!')
        branchList = []
        for i in data['branch_lists']:
            branchList.append([InlineKeyboardButton(
                text=f"{i}", callback_data=f"$branch_"+i)])
        branchList.append([InlineKeyboardButton(
            text="그만두기", callback_data="END")])
        brMarkup = InlineKeyboardMarkup(branchList)

        update.message.reply_text(
            '먼저 브랜치를 골라줘!', reply_markup=brMarkup)
        # update.message.reply_text("먼저 브랜치를 골라줄래?", reply_markup=brMarkup)
        return BRANCH

    except(IndexError, ValueError):
        update.message.reply_text(
            'https://githubell.netlify.app/ 에서 깃허브 레포지토리를 등록할수있어!')
        update.message.reply_text(
            '/start 명령어로 언제든지 날 불러줘!')
        return CHOOSE


# 브랜치 선택에 대한 대답 (BRANCH)


def branch(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = p.match(query.data).group(1)
    query.answer()
    bot.send_message(chat_id=query.message.chat_id, text=f'{data} 브랜치를 골랐구나?')
    context.user_data[2] = data
    # print(context.user_data)
    text = "이제 별명을 입력해줘!"
    bot.send_message(chat_id=query.message.chat_id, text=text)
    bot.send_message(chat_id=query.message.chat_id,
                     text='/skip 을 치면 별명 설정은 생략될거야!')

    return TYPING


def skip_alias(update: Update, context: CallbackContext) -> None:
    bot.send_message(chat_id=update.message.chat.id,
                     text=f'알겠어! 기본 레포지토리 이름인 {context.user_data[1]}으로 등록해둘게!')
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
    send_data = {'id': context.user_data[0],  # 유저 아이디
                 'fav_repository': context.user_data[4],  # 레포주소
                 'nick_name': context.user_data[3],  # 레포 별명
                 'type': 'telegram',
                 'branch': context.user_data[2]}  # 선택 브랜치
    # print(send_data)
    response = requests.post(
        url='http://margarets.pythonanywhere.com/api/', data=send_data)
    # print(response)
    bot.send_message(chat_id=query.message.chat.id,
                     text=f'{context.user_data[3]} 레포지토리가 성공적으로 등록됐어! 이제 새로운 업데이트가 생기면 내가 알려줄게!')
    print(context.user_data)
    return CHOOSE


def repoStatus(update: Update, context: CallbackContext):  # 레포리스트를 가져와서 고르는 함수
    #print('active repoStatus')
    repoList = []
    res = requests.get(
        f"http://margarets.pythonanywhere.com/api/alias/?id={update.effective_chat.id}")
    res = json.loads(res.content)
    # print(update)
    resLength = len(res['alias'])
    if(len(res['alias']) == 0):
        update.message.reply_text("아직 등록된 브랜치가 없는것같아...😢")
        update.message.reply_text(
            "🔔 https://githubell.netlify.app/ 에서 깃허브 레포지토리를 등록할수있어!")
        return CHOOSE
    else:
        for i in range(0, resLength):
            repoList.append([InlineKeyboardButton(
                text=f"{res['alias'][i]}", callback_data=f"$Check_{res['alias'][i]}")])
        repoMarkup = InlineKeyboardMarkup(repoList)
        update.message.reply_text("원하는 레포별명을 선택해줄래?", reply_markup=repoMarkup)
        return STATUS


def end(update: Update, context: CallbackContext) -> None:
    bot.send_message(chat_id=update.callback_query.message.chat.id,
                     text='레포지토리 등록이 중단되었어:(')
    return CHOOSE


def farewell(update: Update, context: CallbackContext) -> None:
    bot.send_message(chat_id=update.message.chat.id,
                     text='너도 안녕!! 다시 내가 필요하면 /start로 날 불러줘!')
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


def callbackGet(update: Update, context: CallbackContext):  # 레포 선택에 대한 대답
    data = {'id': f'{update.effective_chat.id}',
            'nick_name': f'{c.match(update.callback_query.data).group(1)}'}
    try:
        res = requests.get(
            "http://margarets.pythonanywhere.com/api/git/", params=data)
        res = json.loads(res.content)
        repoURL = res['repoUrl']
        repoBRANCH = res['repoBranch']
        data2 = {'id': f'{update.effective_chat.id}', 'nick_name': f'{c.match(update.callback_query.data).group(1)}',
                 'fav_repository': f'{repoURL}', 'type': 'telegram', 'branch': f'{repoBRANCH}'}
        res2 = requests.get(
            "http://margarets.pythonanywhere.com/api/", params=data2)
        res2 = json.loads(res2.content)

        if res2 == []:
            return_res2 = "해당 레포 업데이트 사항이 없네..:d"
        elif res2 == None:
            return_res2 = "해당 레포 업데이트 사항이 없어..:("
        else:
            ISO = res2[0].get("commit").get("committer").get("date")
            KST = changeKST(ISO)
            return_res2 = f"[{update.callback_query.data}] 최근 커밋 이력이야!.\n"
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
        return CHOOSE
    except IndexError:
        print(IndexError)
        bot.send_message(chat_id=update.message.chat.id,
                         text='무슨 문제가 생겼나봐! 나중에 다시 시도해줘!')
        return CHOOSE


def howto(update: Update, context: CallbackContext):
    # print('사용방법')
    bot.send_message(chat_id=update.message.chat.id,
                     text='관심있거나 소식받고싶은 레포지토리가 있니?')
    bot.send_message(chat_id=update.message.chat.id,
                     text='https://githubell.netlify.app/ 에서 깃허브 레포지토리를 등록할수있어!')
    bot.send_message(chat_id=update.message.chat.id,
                     text='깃허벨 홈페이지에서 만든 큐알코드를 인식 어플로 인식시켜주면 내가 기억해둘게!')
    return CHOOSE
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
#print('start main')
updater = Updater(token=TOKEN, use_context=True)

updater = Updater(TOKEN)

dispatcher = updater.dispatcher

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        BRANCH: [CallbackQueryHandler(branch, pattern=p)],
        ALIAS: [CallbackQueryHandler(saveAlias, pattern='^(?!\/skip).*$')],
        TYPING: [MessageHandler(Filters.text & ~Filters.command, saveAlias), CommandHandler('skip', skip_alias)],
        SEND: [CallbackQueryHandler(send, pattern='^SEND$')],
        STATUS: [(CallbackQueryHandler(callbackGet, pattern=c))],
        CHOOSE: [MessageHandler(Filters.regex('^(사용방법)$'), howto), MessageHandler(
            Filters.regex('^레포지토리 상태 확인$'), repoStatus), MessageHandler(
            Filters.regex('^작별인사$'), farewell)]
    },
    fallbacks=[CallbackQueryHandler(end, pattern='^END$')],

    per_user=True,
    conversation_timeout=3600,
)
dispatcher.add_handler(conv_handler)
# dispatcher.add_handler(CallbackQueryHandler(callbackGet, pattern=c))

updater.start_polling(timeout=10, poll_interval=1, clean=True)

```

## 유저 새 레포지토리 등록 요청

유저가 서버에 새 레포지토리를 등록하는 요청입니다

```json
POST "http://margarets.pythonanywhere.com/api/"
```

| 파라미터         |                의미                 |
| ---------------- | :---------------------------------: |
| `id`             |       등록된 유저 아이디 정보       |
| `fav_repository` | 등록된 유저가 관심등록한 레파지토리 |
| `nick_name`      |        유저가 등록한 닉네임         |
| `type`           |              sns 타입               |
| `branch`         |     관심 레파지토리의 브랜치명      |

**성공시:**

```json
HTTP/1.1 200
Server: margarets.pythonanywhere.com
Content-Type: application/json
{
    "정상적으로 api 호출 완료"
}
```

**실패시:**

```json
HTTP/1.1 404
Server: margarets.pythonanywhere.com
Content-Type: application/json
{
    "정상적이지 않은 {변수 이름} 입니다"
}
```

## 유저기 요청한 닉네임 레포지토리의 실제 레포지토리 정보 요청

유저가 저장한 별명 레포지토리의 실제 정보를 가져오는 요청입니다.\
새로운 정보가 갱신되었는지 확인하기 전에 먼저 실행되는 api 요청함수입니다

**요청:**

```json
GET "http://margarets.pythonanywhere.com/api/git/?id={id}&&nick_name={nick_name}}"
```

| 파라미터    |          의미           |
| ----------- | :---------------------: |
| `id`        | 등록된 유저 아이디 정보 |
| `nick_name` |  유저가 등록한 닉네임   |

**성공시:**

```json
HTTP/1.1 200
Server: margarets.pythonanywhere.com
Content-Type: application/json
{
    "repoUrl": "https://github.com/margarets-kim/telegram_githubell",
    "repoBranch": "main"
}
```

**실패시:**

```json
HTTP/1.1 200
Server: margarets.pythonanywhere.com
Content-Type: application/json
{
    "repoUrl": [], //빈 배열 리턴
    "repoBranch": []
}
}
```

## 유저 레포지토리 저장 정보 요청

변경사항이 있는지 앞서 실제 레포지토리의 정보를 들고온 후 기존 DB와 비교 요청을 하는 api 요청 함수입니다

**요청:**

```json
GET "http://margarets.pythonanywhere.com/api/?{Params}"
```

| 파라미터         |                의미                 |
| ---------------- | :---------------------------------: |
| `id`             |       등록된 유저 아이디 정보       |
| `fav_repository` | 등록된 유저가 관심등록한 레파지토리 |
| `nick_name`      |        유저가 등록한 닉네임         |
| `type`           |              sns 타입               |
| `branch`         |     관심 레파지토리의 브랜치명      |

**성공시:**

```json
HTTP/1.1 200
Server: margarets.pythonanywhere.com
Content-Type: application/json
[
    {
        "sha": "e26c844322f0f7b2b045484532c601f114384792",
        "node_id": "MDY6Q29tbWl0MzE5NDMxMjU1OmUyNmM4NDQzMjJmMGY3YjJiMDQ1NDg0NTMyYzYwMWYxMTQzODQ3OTI=",
        "commit": {
            "author": {
                "name": "margarets-kim",
                "email": "margarets.urssu@gmail.com",
                "date": "2020-12-08T18:04:57Z"
            },
            "committer": {
                "name": "margarets-kim",
                "email": "margarets.urssu@gmail.com",
                "date": "2020-12-08T18:04:57Z"
            },
            "message": "final",
            "tree": {
                "sha": "c8a13682a940e58da997992b935b715c8ae9a2a6",
                "url": "https://api.github.com/repos/margarets-kim/telegram_githubell/git/trees/c8a13682a940e58da997992b935b715c8ae9a2a6"
            },
            "url": "https://api.github.com/repos/margarets-kim/telegram_githubell/git/commits/e26c844322f0f7b2b045484532c601f114384792",
            "comment_count": 0,
            "verification": {
                "verified": false,
                "reason": "unsigned",
                "signature": null,
                "payload": null
            }
        },
        "url": "https://api.github.com/repos/margarets-kim/telegram_githubell/commits/e26c844322f0f7b2b045484532c601f114384792",
        "html_url": "https://github.com/margarets-kim/telegram_githubell/commit/e26c844322f0f7b2b045484532c601f114384792",
        "comments_url": "https://api.github.com/repos/margarets-kim/telegram_githubell/commits/e26c844322f0f7b2b045484532c601f114384792/comments",
        "author": {
            "login": "margarets-kim",
            "id": 71299486,
            "node_id": "MDQ6VXNlcjcxMjk5NDg2",
            "avatar_url": "https://avatars0.githubusercontent.com/u/71299486?v=4",
            "gravatar_id": "",
            "url": "https://api.github.com/users/margarets-kim",
            "html_url": "https://github.com/margarets-kim",
            "followers_url": "https://api.github.com/users/margarets-kim/followers",
            "following_url": "https://api.github.com/users/margarets-kim/following{/other_user}",
            "gists_url": "https://api.github.com/users/margarets-kim/gists{/gist_id}",
            "starred_url": "https://api.github.com/users/margarets-kim/starred{/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/margarets-kim/subscriptions",
            "organizations_url": "https://api.github.com/users/margarets-kim/orgs",
            "repos_url": "https://api.github.com/users/margarets-kim/repos",
            "events_url": "https://api.github.com/users/margarets-kim/events{/privacy}",
            "received_events_url": "https://api.github.com/users/margarets-kim/received_events",
            "type": "User",
            "site_admin": false
        },
        "committer": {
            "login": "margarets-kim",
            "id": 71299486,
            "node_id": "MDQ6VXNlcjcxMjk5NDg2",
            "avatar_url": "https://avatars0.githubusercontent.com/u/71299486?v=4",
            "gravatar_id": "",
            "url": "https://api.github.com/users/margarets-kim",
            "html_url": "https://github.com/margarets-kim",
            "followers_url": "https://api.github.com/users/margarets-kim/followers",
            "following_url": "https://api.github.com/users/margarets-kim/following{/other_user}",
            "gists_url": "https://api.github.com/users/margarets-kim/gists{/gist_id}",
            "starred_url": "https://api.github.com/users/margarets-kim/starred{/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/margarets-kim/subscriptions",
            "organizations_url": "https://api.github.com/users/margarets-kim/orgs",
            "repos_url": "https://api.github.com/users/margarets-kim/repos",
            "events_url": "https://api.github.com/users/margarets-kim/events{/privacy}",
            "received_events_url": "https://api.github.com/users/margarets-kim/received_events",
            "type": "User",
            "site_admin": false
        },
        "parents": [
            {
                "sha": "637320c780e5d5740d16bee8d046ca1f020f2206",
                "url": "https://api.github.com/repos/margarets-kim/telegram_githubell/commits/637320c780e5d5740d16bee8d046ca1f020f2206",
                "html_url": "https://github.com/margarets-kim/telegram_githubell/commit/637320c780e5d5740d16bee8d046ca1f020f2206"
            }
        ]
    }
]
```

**실패시:**

```json
HTTP/1.1 200
Server: margarets.pythonanywhere.com
Content-Type: application/json
{
    [] //빈 배열 반환
}

```

# 텔레그램 봇을 위한 Always on Task Polling 기능

## 프로그램 개요

텔레그램봇은 크게 두가지로 나뉘는데, 계속 유저들의 메세지를 Listen하는 Polling방식과, Web hook과 연동시켜 api로 봇을 운영할 수 있습니다. \
깃허벨은 업데이트된 레포지토리를 바로 알려야하기 때문에 Polling 방식으로 구현되었으며,
해당 기능을 사용하기 위해 Pythonanywhere에서 지원하는 Awlays on Task 기능에 서버 구동 스크립트를 실행시켰습니다. \
따라서 텔레그램봇은 웹앱이 존재하지않으며 Polling을 하는 파이썬 파일로 구동되고있습니다.
