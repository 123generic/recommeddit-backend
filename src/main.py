#!/usr/bin/python3
import json, sys, requests, recommendations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

""" GLOBALS """
ERROR_MESSAGE = {"error_message": "No query", "success": False, "recommendations": []}

@app.get("/suggest")
def auto_suggest(query):
    if query == '':
        return [{"suggest": ''}, 200, {'Access-Control-Allow-Origin': '*'}]

    cursorPoint = len(query) + 1
    newQuery = "%20".join(query.split())

    url = "https://www.google.com/complete/search?q={}%20reddit&cp={}&client=gws-wiz&xssi=t&hl=en&authuser=0&dpr=2".format(newQuery, cursorPoint)

    res = requests.get(url).text[5:]
    parsed = json.loads(res)[0]

    newResult = [element[0].replace("reddit", "") for element in parsed]

    return [{"suggest": newResult}, 200, {'Access-Control-Allow-Origin': '*'}]

@app.get("/search")
def search(query):
    if query == '':
        return ERROR_MESSAGE
    try:
        r = recommendations.get_recommendations(query)
        return {"success":True, "recommendations":r}
    except:
        #  oh well
        return {"success":False, "recommendations":'', "error_message":'we\'re overwhelmed, try again later'}

@app.get("/debug")
def debug():
    return {"success":True}

def main():
    # assume first argument is query. Default query is 'C++ IDE'
    try:
        query = sys.argv[1]
    except IndexError:
        query = "Best C++ IDE"

    results = recommendations.get_recommendations(query)

    print(results)