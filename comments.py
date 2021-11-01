import os

from dotenv import load_dotenv
from pmaw import PushshiftAPI

load_dotenv(".env")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
USER_AGENT = os.getenv("USER_AGENT")

api = PushshiftAPI()

ID_LENGTH = 6


def comment_to_dict(comment):
    return {
        "text": comment.get("body", ""),
        "score": comment.get("score", 0),
        "url": "https://www.reddit.com" + comment.get("permalink", ""),
    }


def get_comments(urls):
    submission_ids = []
    for url in urls:
        i = url.find("/comments/") + len("/comments/")
        submission_ids.append(url[i:i + ID_LENGTH])

    comment_ids = api.search_submission_comment_ids(ids=submission_ids)
    comments = api.search_comments(ids=comment_ids)

    return comments
