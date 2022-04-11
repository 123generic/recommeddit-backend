import os

from dotenv import load_dotenv
from serpapi import GoogleSearch

load_dotenv(".env")
serp_api_key = os.getenv("SERPAPI_API_KEY")

# params for serp_image api
params = {
    "q": [],
    "tbm": "isch",
    "ijn": "0",
    "api_key": serp_api_key
}


# function to get images/description of images
# based off a list of recommendations and keywords extracted from query
def get_images(name, category):
    params["q"] = name + " " + category
    search = GoogleSearch(params)
    results = search.get_dict()
    images_results = results['images_results']
    return [img['original'] for img in images_results[:5]]
