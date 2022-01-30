import concurrent.futures
import html
import re

import requests

"""
Uses regex to parse comments from requests object
"""


def parse_info(request_object):
    text = request_object.text
    comments = re.findall(r'"body": "(.*?)"', text)  # todo: preprocess comments
    if len(comments) == 0:  # If no comments, nothing to do
        return None
    scores = re.findall(r'"score":(.*?),', text)[1:]  # Ignore: first score is score of the thread
    links = re.findall(r'"permalink": "(.*?)",', text)[1:]  # Ignore: see above
    if not len(comments) == len(scores) == len(links):
        raise Exception('Unexpected thread format: link = {0}'.format(request_object.url))
    return [{'text': html.unescape(c), 'score': s, 'url': l} for c, s, l in zip(comments, scores, links)]


"""
Calls get_basic_info and parse_comments. Assembles their results into a list
of lists of the form [[title, text, score, num comments, comment] x N].
"""


def assemble_thread_info(url, header):
    try:
        json_tree = requests.get(url + '.json?limit=200', headers=header)
    except:
        print('caught a bad url')
        return None
    return parse_info(json_tree)


"""
Creates a thread to all assemble_thread_info for each URL passed to it.
"""


def thread_builder(urls, headers):
    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(urls)) as exec:
        futures = [exec.submit(assemble_thread_info, url, headers) for url in urls]
        for future in futures:
            result = future.result()
            if result is not None:
                rows.extend(result)
    return rows


def comment_to_dict(comment):
    return {
        "text": comment.get("body", ""),
        "score": comment.get("score", 0),
        "url": "https://www.reddit.com" + comment.get("permalink", ""),
    }


def get_comments(urls):
    comments = thread_builder(urls, {'User-agent': 'Recommeddit-Bot 0.101'})
    return comments
