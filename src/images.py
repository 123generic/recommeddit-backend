import re, requests, os
from serpapi import GoogleSearch
from dotenv import load_dotenv
# from googleapiclient.discovery import build

load_dotenv(".env")
# my_api_key = os.getenv("SEARCH_PY_API_KEY")
# cx_key = os.getenv("CX_KEY")
serp_api_key = os.getenv("SERPAPI_API_KEY")

# resource = build("customsearch", "v1", developerKey=my_api_key).cse()

# Regex for links
links = re.compile(r'<div class="egMi0 kCrYT"><a href="/url\?q=(.*?)&amp;')

# Parameters for serpapi
params = {
    "q": [],
    "tbm": "isch",
    "ijn": "0",
    "api_key": serp_api_key
}


# function to get images/description of images
# based off a list of recommendations and keywords extracted from query
def get_images(name, category, rec):
    params["q"] = name + " " + category
    search = GoogleSearch(params)
    results = search.get_dict()
    images_results = results['images_results']
    return [img['original'] for img in images_results[:5]], rec

# def get_links(query, nouns, rec):
#     # http = google_auth_httplib2.AuthorizedHttp(credentials, http=httplib2.Http())
#     s = query + nouns
#     result = resource.list(q=s, cx=cx_key).execute(http=httplib2.Http())
#     return result['items'][0]['link'], rec