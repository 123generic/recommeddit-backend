import os

# the hide api key bs
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv(".env")
my_api_key = os.getenv("SEARCH_PY_API_KEY")
cx_key = os.getenv("CX_KEY")
################################################################

resource = build("customsearch", "v1", developerKey=my_api_key).cse()


# search google with string and make sure has reddit in it
# return list of urls with reddit links
# they will do their magic with the reddit links


def return_links(search_string):
    if not search_string.endswith(" reddit"):
        search_string += " reddit"
    result = resource.list(q=search_string, cx=cx_key).execute()
    links = []
    for item in result["items"]:
        url = item["link"]  # link is exact url
        domain = item["displayLink"]  # displayLink is domain
        if domain.endswith("reddit.com") and "comments" in url:
            links.append(url)
    return links


def return_top_result(search_string):
    result = resource.list(q=search_string, cx=cx_key).execute()
    return result["link"][0]  # link is exact url
