import spacy, concurrent.futures
from json_parser import parse
from scoring import calc_points
from scraper import scrape_reddit_links_from_google_query, scrape_json_from_reddit_links
from Wikidup import top_wikidata, matching
from cross_reference import gkg_query

# Loading spacy pipeline
spacy.require_gpu()
NLP = spacy.load('roberta-model-best')
nouns_nlp = spacy.load('en_core_web_lg', disable=['parser','ner','lemmatizer'])
# NLP = spacy.load('tok2vec')
NLP.add_pipe('sentencizer')

def get_recommendations(query):
    """
    Main entry function. Requires that query be valid in some way. Returns recommendation objects
    query: query to search for
    returns: list of recommendation objects
    """
    # Get nouns in query
    user_query_nouns = ' '.join([tok.text for tok in nouns_nlp(query) if tok.pos_ in ['PPN', 'NN']])

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
        lst.append(calc_points(lst[1]))  # [[ent, comment, score], ...]
    ents.sort(key=lambda x: x[2], reverse=True)  # Sort by score

    # From here, put in loop and wait until ten received
    # De-Dupe and Consolidate (obtain wikidata ID and real name)
    # Cross reference remaining
    recommendations = _de_dupe(ents[:100])
    recommendations = _cross_ref(recommendations, user_query_nouns)

    # Return in dict format
    return sorted([r.to_dict() for r in recommendations], key=lambda x: x['score'], reverse=True)


def _get_entities(comments):
    entities = []
    for comment in comments:
        for entity in comment.ents:
            entities.append([entity, comment])
    return entities


def _de_dupe(entities):
    # Call wikidup wrapper in parallel for all ten entities
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(entities)) as exec:
        futures = [exec.submit(top_wikidata, entity, 5) for entity, _, _ in entities]
        results = [x.result() for x in futures]
    named_wids, named_ents, named_scores, named_comments, nameless = [], [], [], [], []  # TODO: Figure out what to do with nameless
    for wids, ent_l in zip(results, entities):
        if not wids: nameless.append(ent_l)
        else: 
            named_wids.append(wids)
            named_ents.append(ent_l[0])
            named_scores.append(ent_l[2])
            named_comments.append(ent_l[1])

    # Sequentially, determine which entities are the same
    recommendations = [r for r in matching(named_wids, named_ents, named_scores, named_comments) if r is not None]
    return recommendations


def _cross_ref(recommendations, user_query_nouns):
    # Cross reference using google knowledge graph
    def gkg_wrapper(query, rec):
        return gkg_query(query), rec
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(recommendations)) as exec:
        futures = [exec.submit(gkg_wrapper, r.entity + user_query_nouns, r) for r in recommendations]
        results = [x.result() for x in futures]
    recs = [r for boolean, r in results if boolean]
    return recs

if __name__ == '__main__':
    print(get_recommendations('best laptop'))