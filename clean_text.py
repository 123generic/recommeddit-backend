"""
Title: clean_text.py
Author: --
Date: --
Description: Function that removes markdown and newlines from comments and titles
"""

from io import StringIO
from markdown import Markdown
from unidecode import unidecode
import html


def _unmark_element(element, stream=None):
    """
    Helper function. Removes markdown from a text input stream.
    element: string to unmark
    returns: markdownless text
    """
    if stream is None:
        stream = StringIO()
    if element.text:
        stream.write(element.text)
    for sub in element:
        _unmark_element(sub, stream)
    if element.tail:
        stream.write(element.tail)
    return stream.getvalue()


# patching Markdown
Markdown.output_formats["plain"] = _unmark_element
__md = Markdown(output_format="plain")
__md.stripTopLevelTags = False


def clean_text(text):
    """
    Universal function to clean text in application. All text should be passed
    through this function before being used.
    text: text to clean
    returns: cleaned text
    """
    t = __md.convert(text)
    return unidecode(html.decode(t.replace('\n',' ')))
