"""
Title: scraper.py
Author: Mehir Arora
Date: April 4th, 2022
Description: Methods to extract google links and json data from reddit via a query 
"""

import re, requests, concurrent.futures

# GLOBALS
HEADER = {'User-agent': 'Recommeddit-Bot 0.101'}
MIN_NUM_OF_RESULTS = 30
MAX_COMMENTS = 200
reddit_re = re.compile(r'https://www\.reddit\.com/r/[\w]+/comments/.*?/')

def _safe_req(link):
    """
    Helper method. Safely requests and returns None if failed.
    link: link to request
    header: header of request to send
    returns: request object or None on exception
    """
    try:
        return requests.get(link, headers=HEADER)
    except:
        print('caught bad url')
        return None

def scrape_reddit_links_from_google_query(query, limit):
    """
    Returns list of reddit urls given a plain text query.
    query: plain text query to search for
    limit: maximum number of links to return
    retuns: list of links
    """

    # Get all links
    words = query.split(' ')
    words.append('site:reddit.com')
    urls = []
    for page in range(0,MIN_NUM_OF_RESULTS + 10, 10):
        url = 'https://www.google.com/search?q=' + '+'.join(words) + '&start=' + str(page)
        urls.append(url)
    
    # Asynchronous requests and scraping
    outputs = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(urls)) as exec:
        futures = [exec.submit(_safe_req, url) for url in urls]
        for future in futures:
            result = future.result()
            if result is not None:
                outputs.extend(reddit_re.findall(result.text))
    return outputs

def scrape_json_from_reddit_links(links):
    """
    Returns parsed json objects from list of links
    links: links to parse for json
    retuns: list of parsed json ouputs
    """
    outputs = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(links)) as exec:
        futures = [exec.submit(_safe_req, url + f'.json?limit={MAX_COMMENTS}') for url in links]
        for future in futures:
            result = future.result()
            if result is not None:
                outputs.append(result)
    return [r.json() for r in outputs]

if __name__ == '__main__':
    links = scrape_reddit_links_from_google_query('best microwave', 20)
    jsons = scrape_json_from_reddit_links(links)