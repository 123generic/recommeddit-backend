from collections import namedtuple

from glom import glom
from selenium import webdriver
from selenium.webdriver.common.by import By

from comments import comment_to_dict
from gsearch import gkg_query, serp
from images import get_images
from search import return_top_result

Bounds = namedtuple('Bounds', "start end")


def populate_extraction(extraction):
    if not extraction.url:
        extraction.url = return_top_result(f"{extraction.name} {extraction.general_category}")
    if extraction.mid and extraction.mid.startswith("/m/"):
        result = gkg_query(extraction.mid)
        if result['name']:
            extraction.name = result.name
        if result['description']:
            extraction.description = result.description
        if result['image_url']:
            extraction.image_urls.append(result.image_url)
    else:
        if extraction.wikidata_entry:
            extraction.name = extraction.wikidata_entry.title
            extraction.description = extraction.wikidata_entry.description
        query = serp(f"{extraction.name} {extraction.general_category}")
        about_page_link = query['organic_results'][0]['about_page_link']
        options = webdriver.FirefoxOptions()
        options.binary_location = r"/Applications/Firefox Developer Edition.app/Contents/MacOS/firefox"
        driver = webdriver.Firefox(executable_path=r'/usr/local/Cellar/geckodriver/0.31.0/bin/geckodriver',
                                   options=options)
        driver.get(about_page_link)
        extraction.description = driver.find_element(by=By.CSS_SELECTOR, value='[jsdata=deferred-i7] > div > div') \
                                     .text.rsplit('.', 1)[0] + '.'
        driver.close()
    if len(extraction.image_urls) <= 1:
        extraction.image_urls.extend(get_images(extraction.name, extraction.general_category))


class Extraction:
    def __init__(self, name, score, comments=None, category=None, general_category=None, description=None, url=None,
                 cross_referenced_url=None, image_urls=None, mid=None, wikidata_entry=None):
        if image_urls is None:
            image_urls = []
        if comments is None:
            comments = []
        self.name = name
        self.score = score
        self.comments = comments
        self.category = category
        self.general_category = general_category
        self.description = description
        self.url = url
        self.cross_referenced_url = cross_referenced_url
        self.image_urls = image_urls
        self.mid = mid
        self.wikidata_entry = wikidata_entry

    # @classmethod
    # def from_dict(cls, d, offset=0):
    #     start, end = [bound + offset for bound in d['offset_span']]
    #     return cls(d['extracted_text'], Bounds(start, end))

    @classmethod
    def from_dict(cls, d):
        mid = glom(d, 'metadata.mid', default=None)
        return cls(d['name'], d['score'], d['comments'], mid=mid)


class ExtractionList:
    def __init__(self, extractions):
        self.extractions = extractions

    # @classmethod
    # def from_chunked_results(cls, chunked_results):
    #     extractions = []
    #     prev_len = 0
    #     for chunked_result in chunked_results:
    #         for extraction in chunked_result['extractions']:
    #             extractions.append(Extraction.from_dict(extraction, offset=prev_len))
    #         prev_len += len(chunked_result['text']) + 2  # we add 2 because there is "\n\n" between comments
    #     return cls(extractions)

    @classmethod
    def from_duped_results(cls, duped_results):
        d = {}
        for duped_result in duped_results:
            key = glom(duped_result, 'metadata.mid', default=duped_result['name'].lower())
            if key not in d:
                d[key] = duped_result
            else:
                d[key]['score'] += duped_result['score']
                d[key]['comments'].extend(duped_result['comments'])
        extractions = []
        for extraction in d.values():
            extractions.append(Extraction.from_dict(extraction))
        return cls(extractions)


class Comment:
    def __init__(self, name, score, url):
        self.name = name
        self.score = score
        self.url = url

    @classmethod
    def from_dict(cls, d):
        return cls(d["text"], int(d["score"]), d["url"])

    def to_dict(self):
        return comment_to_dict(self)

    def __str__(self):
        return self.name


class CommentList:
    def __init__(self, comments):
        # self.bounds_list = [Bounds(0, 0)] * len(comments)
        self.comments = comments
        # self.set_bounds()

    # def chunk(self, limit=42000):
    #     next_chunk_start_index = next((i for i, bounds in enumerate(self.bounds_list) if bounds.end >= limit),
    #                                   None)
    #     if next_chunk_start_index is None:
    #         return [ChunkedComment(self.comments)]
    #     next_chunk = CommentList(self.comments[next_chunk_start_index:])
    #     return [ChunkedComment(self.comments[:next_chunk_start_index])] + next_chunk.chunk()

    # def add_extraction(self, extraction):
    #     offset_start, offset_end = extraction.bounds
    #     for i, bounds in enumerate(self.bounds_list):
    #         if bounds.start <= offset_start < bounds.end:
    #             start = offset_start - bounds.start
    #             end = offset_end - bounds.start
    #             self.comments[i].extractions.append(Extraction(extraction.name, Bounds(start, end)), None, None, [])
    #             return

    def to_list(self):
        return self.comments

    # def set_bounds(self):
    #     for i, comment in enumerate(self.comments):
    #         if i == 0:
    #             offset = 0
    #         else:
    #             offset = self.bounds_list[i - 1].end + 2  # we add 2 because there is "\n\n" between comments
    #         self.bounds_list[i] = Bounds(offset, offset + len(str(comment)))

# class ChunkedComment(CommentList):
#     def __init__(self, comments):
#         super().__init__(comments)
#
#     def __str__(self):
#         text = ""
#         for comment in self.comments[:-1]:
#             text += str(comment) + "\n\n"
#         text += str(self.comments[-1])
#
#         return text
