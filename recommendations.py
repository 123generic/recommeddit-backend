import html

from functional import seq
from unidecode import unidecode

import MonkeyLearnProductSentiment
import markdown_to_plaintext
import search
from comment import Comment, CommentList
from comments import get_comments


def clean_comment(comment):
    comment["text"] = unidecode(markdown_to_plaintext.unmark(html.unescape(comment["text"])))
    return comment


def get_recommendations(query):
    if not query:
        return {"error_message": "No query", "success": False, "recommendations": []}

    # search google for "<query name> reddit"
    reddit_urls = search.return_links(query)

    # resolve reddit URLs to comments and remove HTML/markdown syntax
    # comments are dictionaries of string text, number score, and string url.
    # reddit = comments.connect()

    # all_comments = dump_comments.load_comments("dump_movies.dumps")

    # chunked_comments = CommentList(
    #     seq(all_comments)
    #         .map(Comment.from_dict)
    #         .to_list()
    # ).chunk()

    comment_list = CommentList(
        seq(get_comments(reddit_urls))
            .map(clean_comment)
            .map(Comment.from_dict)
            .to_list()
    )

    results = MonkeyLearnProductSentiment.recommendation_extractor_chunked(comment_list, query)

    def convert2serialize(obj):
        if isinstance(obj, dict):
            return {k: convert2serialize(v) for k, v in obj.items()}
        elif hasattr(obj, "_ast"):
            return convert2serialize(obj._ast())
        elif not isinstance(obj, str) and hasattr(obj, "__iter__"):
            return [convert2serialize(v) for v in obj]
        elif hasattr(obj, "__dict__"):
            return {
                k: convert2serialize(v)
                for k, v in obj.__dict__.items()
                if not callable(v) and not k.startswith('_')
            }
        else:
            return obj

    return {"error_message": "", "success": True, "recommendations": convert2serialize(results)}
