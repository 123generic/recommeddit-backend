# hide api
import os
import time
from collections import defaultdict

from dotenv import load_dotenv
from functional import seq
from monkeylearn import MonkeyLearn

import comment_sentiment
import cross_reference
import dedupe
import util
from comment import ExtractionList

load_dotenv(".env")
api_key = os.getenv("URL_SCRAPE_API_KEY")
################################################################

# temporary using api key, change this to .env later on
ml = MonkeyLearn(api_key)


def returnMonkey(data):
    # model id for Product Sentiment
    model_id = "cl_TWmMTdgQ"
    result = ml.classifiers.classify(model_id, data)

    return result.body[0]["classifications"][0]


# print(returnMonkey(['This is the best IDE']))
def returnPositiveorNot(data):
    # will return either positive neutral or negative
    PositiveorNot = returnMonkey(data)["tag_name"]
    return PositiveorNot


# print(returnPositiveorNot(['This is the best IDE']))


def returnConfidence(data):
    # returns confidence in percentage
    confidence = returnMonkey(data)["confidence"]
    # confidence = "{:.1%}".format(0.999)
    return confidence


# print(returnConfidence(['laughing out loud']))

################################################################
# seperate data into strings


def seperate_into_strings(text):
    # uses monkeylearn to extract OPINION units from text
    # text is our input, a big reddit comment that may have multiple sentences
    model_id = "ex_N4aFcea3"
    result = ml.extractors.extract(model_id, text)
    # total is the extractions
    total = result.body[0]["extractions"]
    # data is an array of parsed sentences of the original text
    data = []
    for i in range(len(total)):
        data.append(total[i]["extracted_text"])
    return data


"""
print(seperate_into_strings(['The hotel has a great location but all in all it was a horrible experience! \
    Only stayed here because it was the pre-accomodation choice for one of our tours but it was terrible. \
        Will never stay here again!'])[0])
"""


################################################################
# THIS USES THE KEYWORD EXTRACTOR I DON'T KNOW HOW WELL THIS WILL WORKS
# MAY HAVE A PROBLEM WITH DETECTING TOO MANY KEYWORDS
# MAYBE I CAN INCLUDE VALUES WITH A CERTAIN AMOUNT OF RELEVANCE
def keyword_extractor(data):
    model_id = "ex_YCya9nrn"
    result = ml.extractors.extract(model_id, data)
    array_of_keywords = []
    # total is the extractions
    total = result.body[0]["extractions"]
    # appends the top value because I think it automatically sorts by relevance
    for i in range(len(total)):
        array_of_keywords.append(total[i]["parsed_value"])
    return array_of_keywords


def keyword_extractor_total(comments):
    model_id = "ex_YCya9nrn"
    data = seq(comments).map(lambda comment: comment["text"]).to_list()
    results = ml.extractors.extract(model_id, data).body

    for comment, result in zip(comments, results):
        comment["extractions"] = result["extractions"]

    recommendations = defaultdict(int)

    for analyzed_comment in results:
        for keyword in analyzed_comment["extractions"]:
            recommendations[keyword["parsed_value"]] += float(keyword["relevance"]) * keyword["count"]

    results = dict(
        sorted(
            recommendations.items(),
            key=lambda item: item[1],
            reverse=True
        )
    )

    return results


def keyword_extractor_chunked(chunked_comments, query):
    model_id = "ex_YCya9nrn"
    data = seq(chunked_comments.chunk()).map(str).to_list()
    results = ml.extractors.extract(model_id, data).body

    # for i, chunked_result in enumerate(results):
    #     for extraction in chunked_result["extractions"]:

    # for chunked_comment, result in zip(chunked_comments, results):
    #     chunked_comment["extractions"] = result["extractions"]

    recommendations = defaultdict(int)

    for chunked_result in results:
        for keyword in chunked_result["extractions"]:
            recommendations[keyword["parsed_value"]] += float(keyword["relevance"]) * keyword["count"]

    results = dict(
        sorted(
            recommendations.items(),
            key=lambda item: item[1],
            reverse=True
        )
    ).items()

    deduped = dedupe.dedupe(seq(results).map(lambda result: result[0]).to_list())
    deduped_results = seq(results).filter(lambda result: result[0] in deduped)

    timeout = 20 * 1000
    start = time.time()
    wiki_results = set()
    wiki_deduped_results = []
    for result in deduped_results:
        if time.time() - start > timeout:
            break
        wiki_result = dedupe.top_wiki(result[0], query)
        if wiki_result:
            wiki_result = wiki_result[0]
        if wiki_result not in wiki_results:
            wiki_results.add(wiki_result)
            wiki_deduped_results.append(result)

    num_results = 0
    category = query.split(' ', 1)[1]
    cross_referenced_results = []
    for iters, result in enumerate(wiki_deduped_results):
        if num_results >= 15 or (iters >= 20 and num_results >= 10) or \
                (iters >= 30 and num_results >= 5) or iters >= 40:
            break
        if cross_reference.with_serp(f"{result[0]} {category}")[0]:
            cross_referenced_results.append(result)
    return cross_referenced_results


def recommendation_extractor_chunked(comment_list, query):
    model_id = "ex_LS5yxu8k"
    data = seq(comment_list.chunk()).map(str).to_list()
    results = ml.extractors.extract(model_id, data).body

    extractions = ExtractionList.from_chunked_results(results)

    for extraction in extractions.extractions:
        comment_list.add_extraction(extraction)

    recommendations = defaultdict(float)

    for comment in comment_list.comments:
        comment_recommendations = comment_sentiment \
            .get_scores(seq(comment.extractions)
                        .map(lambda extraction: extraction.text)
                        .to_list(),
                        comment.text,
                        int(comment.score))
        for recommendation, score in util.chunks(comment_recommendations, 2):
            recommendations[recommendation] += score

    results = dict(
        sorted(
            recommendations.items(),
            key=lambda item: item[1],
            reverse=True
        )
    ).items()

    deduped = dedupe.dedupe(seq(results).map(lambda result: result[0]).to_list())
    deduped_results = seq(results).filter(lambda result: result[0] in deduped)

    timeout = 20 * 1000  # 20 seconds
    start = time.time()
    wiki_results = set()
    wiki_deduped_results = []
    for result in deduped_results:
        if time.time() - start > timeout:
            break
        wiki_result = dedupe.top_wiki(result[0], query)
        if wiki_result:
            wiki_result = wiki_result[0]
        if wiki_result not in wiki_results:
            wiki_results.add(wiki_result)
            wiki_deduped_results.append(result)

    num_results = 0
    category = query.split(' ', 1)[1]
    cross_referenced_results = []
    for iters, result in enumerate(wiki_deduped_results):
        if num_results >= 15 or (iters >= 20 and num_results >= 10) or \
                (iters >= 30 and num_results >= 5) or iters >= 40:
            break
        if cross_reference.with_serp(f"{result[0]} {category}")[0]:
            cross_referenced_results.append(result)
    return cross_referenced_results


def movie_extractor_chunked(chunked_comments):
    model_id = "ex_8vwmUB7s"
    # data = seq(chunked_comments).map(lambda chunk: str(chunk)).to_list()
    # results = ml.extractors.extract(model_id, data).body
    #
    # recommendations = defaultdict(int)
    #
    # for chunked_result in results:
    #     for keyword in chunked_result["extractions"]:
    #         recommendations[keyword["parsed_value"]] += 1
    #
    # unfiltered_results = dict(
    #     sorted(
    #         recommendations.items(),
    #         key=lambda item: item[1],
    #         reverse=True
    #     )
    # )
    #
    # count = 0
    # results = []
    # for entry in unfiltered_results.items():
    #     if count == 10:
    #         break
    #     if cross_reference_imdb(entry):
    #         count += 1
    #         results.append(entry)
    #
    # return results
