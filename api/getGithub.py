import json
from urllib.request import urlopen


def bracnhGet(owner, repo):
    try:
        response = urlopen(
            "https://margarets.pythonanywhere.com/api/info/?id="+owner+"&repo="+repo).read().decode('utf-8')
        responseJson = json.loads(response)
        # print(responseJson)
        return responseJson
    except(IndexError, ValueError):
        print(error)


def urlGet(id):
    try:
        response = urlopen(
            "https://api.github.com/repositories/" + id).read().decode('utf-8')
        responseJson = json.loads(response)

        repo = responseJson["name"]
        owner = responseJson["owner"]["login"]
        result = bracnhGet(owner, repo)
        return (owner, repo)
    except(IndexError, ValueError):
        return('error')
