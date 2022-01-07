#!/usr/bin/python
import requests
import sys
import json
import asyncio
import recommendations


def auto_suggest(request):
    if request.args and 'query' in request.args:
        query = request.args.get('query')
    else:
        query = "best youtube"

    cursorPoint = len(query)+1
    newQuery = "%20".join(query.split())

    url = "https://www.google.com/complete/search?q={}%20reddit&cp={}&client=gws-wiz&xssi=t&hl=en&authuser=0&dpr=2".format(newQuery, cursorPoint)

    res = requests.get(url).text[5:]
    parsed = json.loads(res)[0]

    newResult = [element[0].replace("reddit", "") for element in parsed]

    return newResult, 200, {'Access-Control-Allow-Origin': '*'}

def search(request):
    if request.args and 'query' in request.args:
        query = request.args.get('query')
    else:
        query = ""
    results = recommendations.get_recommendations(query)

    return {"suggest": results}, 200, {'Access-Control-Allow-Origin': '*'}


def main():
    # assume first argument is query. Default query is 'C++ IDE'
    try:
        query = sys.argv[1]
    except IndexError:
        query = "Best C++ IDE"

    results = asyncio.run(recommendations.get_recommendations(query))
    suggestions = auto_suggest(query)

    print(results)
    print(suggestions)

if __name__ == "__main__":
    main()
