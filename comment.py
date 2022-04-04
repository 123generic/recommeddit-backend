"""
Title: comment.py
Author: Mehir Arora
Date: April 4th, 2022
Description: Two helper classes to represent Reddit Threads and Comments respectively.
"""

class Thread:
    """
    A class to hold thread information. Contains a pointer to array of
    top level comments.
    """
    def __init__(self, **kwargs):
        self.comments = []  # top level only
        self.all_comments = []  # all comments, unordered
        self.subreddit = kwargs['subreddit']
        self.selftext = kwargs['selftext']
        self.title = kwargs['title']
        self.downs = kwargs['downs']
        self.ups = kwargs['ups']
        self.score = kwargs['score']
        self.upvote_ratio = kwargs['upvote_ratio']
        self.author = kwargs['author']
        self.author_fullname = kwargs['author_fullname']
        self.subreddit_name_prefixed = kwargs['subreddit_name_prefixed']
        self.over_18 = kwargs['over_18']
        self.url = kwargs['url']
        self.permalink = kwargs['permalink']
        self.id = kwargs['id']
        self.num_comments = kwargs['num_comments']
    
    def __repr__(self):
        return f'({self.title[:30]}...,{self.author},{self.score},{self.url},{self.permalink})'


class Comment:
    """
    A class to hold information about a given comment. Contains pointers
    to parent thread, parent comment, and an array of child comments.
    """
    def __init__(self, **kwargs):
        self.parent_thread = None  # common to every element of tree
        self.parent_comment = None  # direct parent in tree
        self.children = []  # all direct replies
        self.subreddit_id = kwargs['subreddit_id']
        self.subreddit = kwargs['subreddit']
        self.id = kwargs['id']
        self.author = kwargs['author']
        self.parent_id = kwargs['parent_id']
        self.score = kwargs['score']
        self.author_fullname = kwargs['author_fullname']
        self.body = kwargs['body']
        self.name = kwargs['name']
        self.ups = kwargs['ups']
        self.downs = kwargs['downs']
        self.permalink = kwargs['permalink']
        self.link_id = kwargs['link_id']
        self.depth = kwargs['depth']
    
    def __repr__(self):
        return f'({self.body[:30]}...,{self.author},{self.score},{self.parent_thread.title[:30]}...,{self.permalink})'