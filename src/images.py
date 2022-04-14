import re, requests, os
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv(".env")
serp_api_key = os.getenv("SERPAPI_API_KEY")

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

def get_links(query, nouns, rec):
    urlparam = '+'.join(query.split(' ') + nouns.split(' '))
    r = requests.get('https://www.google.com/search?q={urlparam}').text
    return links.findall(r)[0], rec