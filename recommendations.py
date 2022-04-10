import spacy

from json_parser import parse
from scoring import calc_points
from scraper import scrape_reddit_links_from_google_query, scrape_json_from_reddit_links

# Loading spacy pipeline
NLP = spacy.load('NER-Model')
NLP.add_pipe('sentencizer')


def get_recommendations(query):
    """
    Main entry function. Requires that query be valid in some way. Returns recommendation objects
    query: query to search for
    returns: list of recommendation objects
    """
    # Scrape google for links
    links = scrape_reddit_links_from_google_query(query)

    # Scrape reddit and parse into dicts from links
    jsons = scrape_json_from_reddit_links(links)

    # Parse dicts for comment objects (text cleaning done in parse method)
    threads = []
    all_comments = []
    for j in jsons:
        thread, comments = parse(j)
        threads.append(thread)
        all_comments.extend(comments)

    # NER and get sentences
    docs = NLP.pipe(x.comment for x in all_comments)
    for comment, doc in zip(all_comments, docs):
        comment.doc = doc
        comment.sentences = [s.text for s in doc.sents]
        comment.ents = [x.text for x in doc.ents]

    # Get all entities [[ent, comment], ...]
    ents = _get_entities(all_comments)

    # Score entities and sort
    for lst in ents:
        lst.append(calc_points(lst[1], lst[1].score))  # [[ent, comment, score], ...]
    ents.sort(key=lambda x: x[2], reverse=True)  # Sort by score

    # From here, put in loop and wait until ten received
    # De-Dupe and Consolidate (obtain wikidata ID and real name)
    # Cross reference remaining
    # recommendations = []
    # while len(recommendations) < 10:
    #     recs = de_dupe(ents[:10])
    #     recs = cross_ref(recs)
    #     recommendations.extend(recs)
    #     ents = ents[10:]

    # Return in dict format
    return ents


def _get_entities(comments):
    entities = []
    for comment in comments:
        for entity in comment.ents:
            entities.append([entity, comment])
    return entities


def de_dupe(entities):
    pass


def cross_ref(entities):
    pass
