"""
Title: clean_text.py
Author: --
Date: --
Description: Function that removes markdown and newlines from comments and titles
"""

from io import StringIO
from markdown import Markdown


def _unmark_element(element, stream=None):
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
    t = __md.convert(text)
    return t.replace('\n',' ')
