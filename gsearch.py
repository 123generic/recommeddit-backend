from __future__ import print_function

import json
import os
import re
import urllib

from dotenv import load_dotenv
from glom import glom
from selenium import webdriver
from selenium.webdriver.common.by import By
from serpapi import GoogleSearch

from util import exists

load_dotenv(".env")

serp_api_key = os.getenv("SERPAPI_API_KEY")
google_knowledge_graph_api_key = os.getenv("GOOGLE_KG_API_KEY")


def serp(query_string):
    params = {
        "q": query_string.lower(),
        "api_key": serp_api_key,
        "hl": "en",
        "gl": "us",
    }

    search = GoogleSearch(params)  # complete Google search with params

    results = search.get_dict()

    return results


def with_serp(query_string):
    """
    with_serp uses the Serp API to provide Google Search results
    The API key is pulled using the config() method from config.py
    Additional help information can be found on `https://serpapi.com/`
    input:
        query_string : type = str, some google search query you want
    output:
        processed_results : type = bool, True if queried results provide reputable answers
                                         False if not
    WARNING: limited queries (100 - 10000)
    """

    params = {
        "q": query_string.lower(),
        "api_key": serp_api_key,
        "hl": "en",
        "gl": "us",
    }

    search = GoogleSearch(params)  # complete Google search with params

    del params  # delete the configuration dictionaries that hold the api key

    results = search.get_dict()
    return process_results(query_string, results)  # check if results are good


def process_results(query_string, results):
    """
    Process the results from the google search query to determine if the queried
    recommendation candidate is acceptable.
    This implementation of process_results checks to see if all query terms are
    included in the web result. This does not consider knowledge graph results.
    input:
        query_string : type = str, the google search query which provided results
        results : type = dict, the results of the Google Search
    output:
        boolean : True if this candidate is acceptable and exists
                  False if not
        link    : type = str, the search result that trusts this candidate
    """
    words = query_string.split(' ')
    for web_result in results['organic_results']:
        count = 0
        for word in words:
            word = word.lower()
            if (exists(web_result, ['about_this_result', 'keywords'])
                and word in [keyword.lower() for keyword in web_result['about_this_result']['keywords']]) or \
                    ('title' in web_result and word in web_result['title'].lower()) or \
                    ('snippet' in web_result and word in web_result['snippet'].lower()):
                count += 1
        if count == len(words):
            return True, web_result['link']
    return False, None


def clean_string(s):
    """
    Clean the string (ie, remove all common punctuation characters)
    input:
        s : type = str, the string that needs to be cleaned
    output:
        str : the processed string
    """
    s = re.sub('["!#$%*]', '', s)  # remove bad chars
    return s


def gkg_query(mid):
    """
    Use Google's Knowledge Graph Search API call and analyze the results to check
    if the output is reasonable for our search query
    input:
        query_string : type = str, some google search query you want
        threshold : type = int, accept all query results which have do not have these
                    many words in their detailed description from the query string,
                    default = 1 -- only one missing word will be tolerated
    """
    params = {
        'ids': mid,
        'limit': 10,
        'indent': True,
        'key': google_knowledge_graph_api_key
    }

    # query KG
    url = 'https://kgsearch.googleapis.com/v1/entities:search' + '?' + urllib.parse.urlencode(params)
    response = json.loads(urllib.request.urlopen(url).read())

    # process results
    result = glom(response, 'itemListElement.0.result', default=None)
    name = glom(result, 'name', default=None)
    description = glom(result, 'detailedDescription.articleBody', default=None)
    image_url = glom(result, 'image.url', default=None)

    if image_url:
        options = webdriver.FirefoxOptions()
        options.binary_location = r"/Applications/Firefox Developer Edition.app/Contents/MacOS/firefox"
        driver = webdriver.Firefox(executable_path=r'/usr/local/Cellar/geckodriver/0.31.0/bin/geckodriver',
                                   options=options)
        driver.get(image_url)
        image_url = driver.find_element(by=By.CSS_SELECTOR, value='.fullImageLink > a').get_attribute('href')
        driver.close()

    return {
        'name': name,
        'description': description,
        'image_url': image_url
    }


if __name__ == '__main__':
    query_string = 'vscode c++ ide'
    # res = serp("vscode ide")
    print(gkg_query('/g/11c3kh6nh5'))
    # print('Query:', query_string, end='\n\n\n\n')
    # res = with_serp(query_string)
    # print(res)
    # if res:
    #     print("SUCCESS")
    # else:
    #     print("FAILURE")
