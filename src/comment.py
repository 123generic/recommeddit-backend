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
        self.cleaned_title = None
        self.downs = kwargs['downs']
        self.ups = kwargs['ups']
        self.score = kwargs['score']
        self.upvote_ratio = kwargs['upvote_ratio']
        self.author = kwargs['author']
        self.subreddit_name_prefixed = kwargs['subreddit_name_prefixed']
        self.over_18 = kwargs['over_18']
        self.url = kwargs['url']
        self.permalink = kwargs['permalink']
        self.id = kwargs['id']
        self.num_comments = kwargs['num_comments']
    
    def __repr__(self):
        return f'({self.title[:30]}...,{self.author},{self.score})'


class Comment:
    """
    A class to hold information about a given comment. Contains pointers
    to parent thread, parent comment, and an array of child comments.
    """
    def __init__(self, **kwargs):
        self.parent_thread = None  # common to every element of tree
        self.parent_comment = None  # direct parent in tree
        self.children = []  # all direct replies
        self.sentences = None # list of sentences for VADER scoring
        self.sentiment_score  = None # score
        self.doc = None
        self.ents = []
        # self.dedupe_name = None
        self.dedupe_image = None  # URL to image
        self.subreddit_id = kwargs['subreddit_id']
        self.subreddit = kwargs['subreddit']
        self.id = kwargs['id']
        self.author = kwargs['author']
        self.parent_id = kwargs['parent_id']
        self.score = kwargs['score']
        self.body = kwargs['body']
        self.comment = None  # cleaned comment
        self.name = kwargs['name']
        self.ups = kwargs['ups']
        self.downs = kwargs['downs']
        self.permalink = kwargs['permalink']
        self.link_id = kwargs['link_id']
        self.depth = kwargs['depth']
    
    def __repr__(self):
        return f'({self.body[:30]}...,{self.score})'

    def to_dict(self):
        return {
            'title':self.parent_thread.title,
            'score':self.score,
            'ups':self.ups,
            'downs':self.downs,
            'body text':self.body,
            'permalink':'www.reddit.com' + self.permalink,
            'author name':self.author
        }

class Recommendation:
    """
    Class to contain a recommendation. Holds an entity and references to many commments
    """
    def __init__(self, entity, wiki_name, wiki_cat, images, score, link, comments, description=None):
        self.entity = entity
        self.wiki_name = wiki_name
        self.wiki_cat = wiki_cat
        self.images = images
        self.score = score
        self.link = link
        self.comments = comments
        self.description = description

    def to_dict(self):
        return {
                'recommendation':self.entity,
                'images':self.images,
                'score':round(self.score, 1),
                'link':self.link,
                'description':self.description,
                'comments':[x.to_dict() for x in self.comments]
            }