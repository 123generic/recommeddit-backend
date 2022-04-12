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
def get_images_and_links(query, rec):
    params["q"] = query
    search = GoogleSearch(params)
    results = search.get_dict()
    images_results = [img['original'] for img in results['images_results'][:3]]
    link = results['images_results'][0]['link']
    rec.images = images_results
    rec.link = link

    return images_results, link, rec