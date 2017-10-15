# reference: Google custom search API client implementations
# link: https://github.com/google/google-api-python-client/blob/master/samples/customsearch/main.py
# author: jcgregorio@google.com (Joe Gregorio)
import json
import re
import os
import urllib
from googleapiclient.discovery import build

import tika
tika.initVM()
from tika import parser

# set DEBUG=True to enable caching
DEBUG = True

"""Search Document class

a document returned by Google search engine, extracted from the 'item' part 
of the JSON data returned by Google search API, including information such as 
the title, URL link, and a snippet of document. Most importantly, the pure 
texts of the webpage are extracted for external use
"""
class SearchDocument(object):
    ## the constructor
    #  @param fields "items" of Google search results, type: dict
    def __init__(self, fields):
        self.title = fields['title']
        self.displink = fields['displayLink']
        self.url = fields['link'] # 'link' is the complete URL, not 'formattedUrl'
        self.snippet = fields['snippet']
        self.key = self.url
        self.text = self.scrape(self.url)

    ## scraping text contents from given URL
    #  @param url URL to visit, type: str
    #  @return text contents, type: str
    def scrape(self, url):
        if not url: return ""

        if DEBUG:
            # cache the scraped results under a local directory for faster debugging
            cache_dir = "scraped"
            if cache_dir and not os.path.exists(cache_dir):
                os.makedirs(cache_dir)
            # use hash value of url string to name the cache file
            fname = "{}/{}.txt".format(cache_dir, abs(hash(url)))
            if os.path.exists(fname):
                with open(fname, 'r') as f:
                    return f.read()
        # END - if DEBUG

        # scrape by retrieving the HTML
        try:
            page = urllib.urlopen(url).read()
        except Exception as e:
            print "failed to open URL, {}".format(e)
            return ""
        
        # calling Apache Tika to extract texts from HTML
        # https://github.com/chrismattmann/tika-python
        contents = parser.from_buffer(page)['content']
        if not contents:
            return ""
        contents = u'\n'.join([c for c in contents.split('\n') if len(c) and not c.isspace()]).encode('ascii', 'ignore')

        if DEBUG:
            # save into local cache file
            with open(fname, 'w') as f:
                f.write(contents)
        # END - if DEBUG
        
        return contents

## execute search and get the JSON formatted result
#  @param api the Google search API key, type: str
#  @param engine the Google search engine ID, type: str
#  @return type: dict
def gsearch_exec(query, api, engine):
    if DEBUG:
        # first try to fetch the search result from saved results on disk,
        # keep in mind that Google charges you fees if you call the API too many times a day!
        # mkdir if necessary
        cache_dir = "searched"
        if cache_dir and not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        fname = cache_dir + '/q_' + '-'.join(query.split()) + '.txt'
        try:
            with open(fname, 'r') as f:
                res = json.load(f)
            return res
        except:
            pass
    # END - if DEBUG

    # Build a service object for interacting with the API. Visit
    # the Google APIs Console <http://code.google.com/apis/console>
    # to get an API key for your own application.
    service = build("customsearch", "v1", developerKey=api)
    res = service.cse().list(q=query, cx=engine).execute()
    
    if DEBUG:
        # save the res into tmp file
        with open(fname, 'w') as f:
            json.dump(res, f)
    # END - if DEBUG

    return res

## apply Google search
#  @param query query terms, type: str
#  @param api the Google search API key, type: str
#  @param engine the Google search engine ID, type: str
#  @return list of returned documents, type: list[SearchDocument]
def gsearch(query, api, engine):
    if not query:
        return []
    raw = gsearch_exec(query, api, engine)
    return [SearchDocument(i) for i in raw['items']]
