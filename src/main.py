#!/usr/bin/python3
import json, sys, requests, recommendations
# from flask import Flask, request
import uvicorn
from fastapi import FastAPI

# app = Flask(__name__)
app = FastAPI()

""" GLOBALS """
ERROR_MESSAGE = {"error_message": "No query", "success": False, "recommendations": []}

@app.get("/suggest")
def auto_suggest(query):
    # if request.args and 'query' in request.args:
    #     query = request.args.get('query')
    # else:
    #     return ERROR_MESSAGE

    cursorPoint = len(query) + 1
    newQuery = "%20".join(query.split())

    url = "https://www.google.com/complete/search?q={}%20reddit&cp={}&client=gws-wiz&xssi=t&hl=en&authuser=0&dpr=2".format(newQuery, cursorPoint)

    res = requests.get(url).text[5:]
    parsed = json.loads(res)[0]

    newResult = [element[0].replace("reddit", "") for element in parsed]

    return [{"suggest": newResult}, 200, {'Access-Control-Allow-Origin': '*'}]

@app.get("/search")
def search(query):
    # if request.args and 'query' in request.args:
    #     query = request.args.get('query')
    # else:
    #     return ERROR_MESSAGE
    return {"success":True, "recommendations":recommendations.get_recommendations(query)}

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


if __name__ == "__main__":
    uvicorn.run("mainak:main")
