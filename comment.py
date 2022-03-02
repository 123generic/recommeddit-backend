from collections import namedtuple

Bounds = namedtuple('Bounds', "start end")


class Extraction:
    def __init__(self, text, bounds):
        self.text = text
        self.bounds = bounds

    @classmethod
    def from_dict(cls, d, offset=0):
        start, end = [bound + offset for bound in d['offset_span']]
        return cls(d['extracted_text'], Bounds(start, end))


class ExtractionList:
    def __init__(self, extractions):
        self.extractions = extractions

    @classmethod
    def from_chunked_results(cls, chunked_results):
        extractions = []
        prev_len = 0
        for chunked_result in chunked_results:
            for extraction in chunked_result['extractions']:
                extractions.append(Extraction.from_dict(extraction, offset=prev_len))
            prev_len += len(chunked_result['text']) + 2  # we add 2 because there is "\n\n" between comments
        return cls(extractions)


class Comment:
    def __init__(self, text, score, url):
        self.text = text
        self.score = score
        self.url = url
        self.extractions = []

    @classmethod
    def from_dict(cls, d):
        return cls(d["text"], d["score"], d["url"])

    def __str__(self):
        return self.text


class CommentList:
    def __init__(self, comments):
        self.bounds_list = [Bounds(0, 0)] * len(comments)
        self.comments = comments
        self.set_bounds()

    def chunk(self, limit=42000):
        next_chunk_start_index = next((i for i, bounds in enumerate(self.bounds_list) if bounds.end >= limit),
                                      None)
        if next_chunk_start_index is None:
            return [ChunkedComment(self.comments)]
        next_chunk = CommentList(self.comments[next_chunk_start_index:])
        return [ChunkedComment(self.comments[:next_chunk_start_index])] + next_chunk.chunk()

    def add_extraction(self, extraction):
        offset_start, offset_end = extraction.bounds
        for i, bounds in enumerate(self.bounds_list):
            if bounds.start <= offset_start < bounds.end:
                start = offset_start - bounds.start
                end = offset_end - bounds.start
                self.comments[i].extractions.append(Extraction(extraction.text, Bounds(start, end)))
                return

    def to_list(self):
        return self.comments

    def set_bounds(self):
        for i, comment in enumerate(self.comments):
            if i == 0:
                offset = 0
            else:
                offset = self.bounds_list[i - 1].end + 2  # we add 2 because there is "\n\n" between comments
            self.bounds_list[i] = Bounds(offset, offset + len(str(comment)))


class ChunkedComment(CommentList):
    def __init__(self, comments):
        super().__init__(comments)

    def __str__(self):
        text = ""
        for comment in self.comments[:-1]:
            text += str(comment) + "\n\n"
        text += str(self.comments[-1])

        return text
