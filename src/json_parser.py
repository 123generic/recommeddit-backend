"""
Title: json_parser.py
Author: Mehir Arora
Date: April 4th, 2022
Description: Contains methods for converting a reddit json tree into thread and comment objects
"""

from comment import Comment, Thread
from clean_text import clean_text

def parse(json):
    """
    Main method to convert from loaded json tree to thread obejct and list of comments.
    json: A reddit json tree parsed into a python dictionary
    returns: (thread, unordered list of all comments)
    """
    thread_head = json[0]['data']['children'][0]['data']
    kwargs = {
        'subreddit':thread_head['subreddit'], 
        'selftext':thread_head['selftext'], 
        'title':thread_head['title'], 
        'downs':thread_head['downs'], 
        'ups':thread_head['ups'], 
        'score':thread_head['score'], 
        'upvote_ratio':thread_head['upvote_ratio'], 
        'author':thread_head['author'], 
        'subreddit_name_prefixed':thread_head['subreddit_name_prefixed'], 
        'over_18':thread_head['over_18'], 
        'url':thread_head['url'], 
        'permalink':thread_head['permalink'], 
        'id':thread_head['id'], 
        'num_comments':thread_head['num_comments']
    }
    the_thread = Thread(**kwargs)
    the_thread.comments, the_thread.all_comments = _get_comments(the_thread, json)
    
    # Clean text of markdown, unicode, html, and  new lines
    the_thread.cleaned_title = clean_text(the_thread.title)
    for comment in the_thread.all_comments:
        comment.comment = clean_text(comment.body)
    return the_thread, the_thread.all_comments

def _get_comments(thread, json):
    """
    Helper function. Converts loaded json tree into a tree of Comment objects and unordered list of all comments.
    thread: The parent thread
    json: A reddit json tree parsed into a python dictionary
    returns: (unordered list of top level comments, unordered list of all comments)
    """
    tree = json[1]['data']['children']
    top_level_comments = []
    all_comments = []
    for listing in tree:
        try: 
            c = listing['data']
            top_level, unrolled_tree = _build_tree(thread, c)
            top_level_comments.append(top_level)
            all_comments.extend(unrolled_tree)
        except:
            pass  # oh well
    return top_level_comments, all_comments

       
def _build_tree(thread, comment):
    """
    Helper function. Given a parent thread and comment tree, returns the top node of a comment object tree
    and the "unrolled" comment tree in unordered list form.
    thread: The parent thread
    comment: The json comment tree head
    returns: (head of comments tree, unordered list of all comment in tree)
    """
    comment_obj = _extract_comment_information(comment)
    comment_obj.parent_thread = thread
    all_comments = []
    all_comments.append(comment_obj)
    if comment['replies'] != '':
        for comm in comment['replies']['data']['children']:
            child, more_comments = _build_tree(thread, comm['data'])
            all_comments.extend(more_comments)
            comment_obj.children.append(child)
    for comm in comment_obj.children:
        comm.parent_comment = comment_obj
    return comment_obj, all_comments

def _extract_comment_information(json_node):
    """
    Helper function. Expects a "comment node" of the json tree and converts a majority
    of the present information into a comment object, save for the replies tree.
    json_node: a subset of the whole comment tree
    returns: a comment object without the replies component of the tree
    """
    kwargs = {
                'subreddit_id':json_node['subreddit_id'], 
                'subreddit':json_node['subreddit'], 
                'id':json_node['id'], 
                'author':json_node['author'], 
                'parent_id':json_node['parent_id'], 
                'score':json_node['score'], 
                'body':json_node['body'], 
                'name':json_node['name'], 
                'downs':json_node['downs'], 
                'ups':json_node['ups'], 
                'permalink':json_node['permalink'], 
                'link_id':json_node['link_id'], 
                'depth':json_node['depth'], 
            }
    return Comment(**kwargs)

if __name__ == '__main__':
    # Debug info only
    import requests
    j = requests.get('https://www.reddit.com/r/MachineLearning/comments/tw9jp5/r_googles_540b_dense_model_pathways_llm_unlocks/.json?limit=500',headers={'user-agent':'my bot 0.001'}).json()
    print(parse(j))