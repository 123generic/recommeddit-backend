import urllib.parse

import requests
import thefuzz.process
from thefuzz import fuzz

THRESHOLD = 90


def dedupe(entries):
    """
    Uses fuzzy matching to remove duplicate entries.
    """
    return thefuzz.process.dedupe(entries, THRESHOLD, fuzz.token_set_ratio)


params = {
    "action": "query",
    "format": "json",
    "prop": "info",
    "list": "search",
    "srsearch": "wikipedia",
    "srlimit": 3,
    "srprop": "sectiontitle"
}

__sources__ = ['wikipedia']


def top_wiki(query, n=3):
    """
    Return the top n results when searching for possible normalized versions of
    the query using the Wikipedia API
    Input:
        - query : type == str, string to be deduped
        - n : the maximum number of possible normalized strings you want
    Output:
        - array, length n, contains only the title of the wikipedia article
    """
    params['srlimit'] = n
    params['srsearch'] = query
    results = \
        requests.get('https://en.wikipedia.org/w/api.php?' + urllib.parse.urlencode(params, doseq=True)) \
            .json()['query']['search']

    return [r['title'] for r in results]
