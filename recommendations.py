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


async def get_recommendations(query):
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

    comments = (seq(reddit_urls)
                .flat_map(get_comments)
                .map(clean_comment)
                .map(Comment.from_dict)
                .to_list())

    chunked_comments = CommentList(
        seq(comments)
            .flatten()
            .map(clean_comment)
            .map(Comment.from_dict)
            .to_list()
    ).chunk()

    results = MonkeyLearnProductSentiment.movie_extractor_chunked(chunked_comments)
    recommendations = seq(results).smap(lambda text, score: {"keyword": text, "score": score}).to_list()

    return {"error_message": "", "success": True, "recommendations": recommendations}
