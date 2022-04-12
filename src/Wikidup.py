from cgi import print_arguments
import requests, re, urllib.parse
from comment import Recommendation

pattern_cat = re.compile('<div class="wikibase-entitytermsview-heading-description ">(.+?)</div>')
pattern_tit = re.compile('<title>(.+?)</title>')

params = {
    "action" : "query",
    "format" : "json",
    "prop" : "categories|categoryinfo|description|duplicatefiles|entityterms|extlinks|extracts|fileusage|globalusage|imageinfo|images|info|iwlinks|langlinks|links|linkshere|mapdata|mmcontent|pageimages|pageprops|pageterms|redirects|pageviews|revisions|templates|transcludedin|videoinfo",
    "list" : "search",
    "srsearch" : "wikipedia",
    "srlimit" : 3,
    "srprop" : "sectiontitle"
}

__sources__ = ['wikipedia']


def top_wiki(query, n=3):
    '''
    Return the top n results when searching for possible normalized versions of
    the query using the Wikipedia API
    Input:
        - query : type == str, string to be deduped
        - n : the maximum number of possible normalized strings you want
    Output:
        - array, length n, contains only the title of the wikipedia article
    '''
    params['srlimit'] = n
    params['srsearch'] = query.lower()
    results = requests.get('https://en.wikipedia.org/w/api.php?' + urllib.parse.urlencode(params, doseq=True)).json()['query']['search']

    return [r['title'] for r in results]


def top_wikidata(query, n=3):
    '''
    Return the top n results when searching for possible normalized versions of
    the query using the Wikipedia API
    Input:
        - query : type == str, string to be deduped
        - n : the maximum number of possible normalized strings you want
    Output:
        - array, length n, contains only the title of the wikipedia article
    '''
    params['srlimit'] = n
    params['srsearch'] = query.lower()
    results = requests.get('https://wikidata.org/w/api.php?' + urllib.parse.urlencode(params, doseq=True)).json()['query']['search']

    return [r['title'] for r in results]


def wikidata(link):
    link = f"https://www.wikidata.org/wiki/{link}"
    data = requests.get(link).text
    t = re.findall(pattern_tit, data)
    c = re.findall(pattern_cat, data)
    title = t[0].split(" - Wikidata")[0] if t else None
    category = c[0] if c else None
    return [title, category]


def matching(wd_ids=[], ents=[], scores=[], comments=[]):
    # [[q1,q2,q3],[q2,a7,q5],[q5,q8,q9]]
    de_ind = [-1 for i in range(len(wd_ids))] # deduped entities
    de_links = ['' for i in range(len(wd_ids))] # deduped entity hashes
    int_lists = []
    for idx in range(len(wd_ids)):
        if de_ind[idx] != -1: # already deduped
            continue
        int_list = [list(set(wd_ids[idx]).intersection(wd_ids[i])) if i != idx else [] for i in range(len(wd_ids))]
        int_lists.append(int_list)
        cmp_len = [len(i) for i in int_list]
        max_cmp = max(cmp_len)
        if max_cmp == 0:    # no similar solutions found by the deduplication process
            de_ind[idx] = ents[idx]
        else:
            # there is a similar solution found by the deduplication process
            max_idx = cmp_len.index(max_cmp)
            index, max_index = min(idx,max_idx), max(idx,max_idx)
            if de_ind[index] != -1:
                de_ind[max_index] = ents[index]
                de_links[max_index] = int_list[max_idx][0]
            else:
                de_ind[index] = ents[index]
                de_ind[max_index] = ents[index]
                de_links[index] = int_list[max_idx][0]
                de_links[max_index] = int_list[max_idx][0]
        if de_links[idx] == '':
            de_links[idx] = wd_ids[idx][0]

    rec_objs = []
    seen = []
    for i in range(len(de_ind)):
        # i = deduped entity
        if de_ind[i] not in seen:
            seen.append(de_ind[i])
            wiki_name, wiki_cat = None, None
            # wiki_name, wiki_cat = wikidata(de_links[i])
            # if scores == []: # filler
            #     scores = [0.0 for i in range(len(ents))]
            # if comments == []: # filler
            #     comments = [['1','2','3'] for i in range(len(ents))]
            rec_objs.append(Recommendation(entity=de_ind[i], images=[], score=scores[i], link=[], comments=[comments[i]], wiki_name=wiki_name, wiki_cat=wiki_cat))
        else:
            rec_objs.append(None) # filler for index purposes
            idx = ents.index(de_ind[i])
            rec_objs[idx].score += scores[i]
            rec_objs[idx].comments.append(comments[i])
    return rec_objs

'''if __name__ == '__main__':
    print([['q1','q2','q3'],['q2','q7','q5'],['q5','q8','q9']])
    print(matching([['q1','q2','q3'],['q2','q7','q5'],['q5','q8','q9']], ['Output 1','Output 2','Output 3']))'''

if __name__ == '__main__':
    # test out wikidata api
    q1 = "visual studio code"
    q2 = "vs code"
    q3 = "clion"
    q4 = "jetbrains clion"
    q5 = "hair dryer"

    res1 = top_wikidata(q1, n=5)
    res2 = top_wikidata(q2, n=5)
    res3 = top_wikidata(q3, n=5)
    res4 = top_wikidata(q4, n=5)
    res5 = top_wikidata(q5, n=5)
    results = [res1,res2,res3,res4,res5]
    entities = [q1,q2,q3,q4,q5]
    for i in range(len(results)):
        print(f"Res{i} {entities[i]}:", results[i])

    output = matching(results, entities)
    print(output)
