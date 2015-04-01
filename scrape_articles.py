"""
Scrape and store citations of retracted pubmed papers.
"""
import sys
import time
import random
import json

import requests 

from scholar import (ScholarQuerier, SearchScholarQuery, csv, ScholarConf,
                     CaptchaError, NotATwoHundredError)

pubmed_search = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&retmax=10000&term=%22retracted%20publication%22[Publication%20Type]'
pubmed_deets = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&rettype=abstract&id='


ScholarConf.LOG_LEVEL = 4

class Error(Exception): pass
class WrongNumberOfResultsError(Error): pass
class TooManyResultsError(Error): pass
class NoResultsError(Error): pass

def load_retracted_articles():
    try: 
        return json.loads(open('retracted.articles.json', 'r').read())
    except ValueError:
        return {}

def save_retracted_articles(articles):
    with open('retracted.articles.json', 'w') as fh:
        fh.write(json.dumps(articles, indent=2))
    return

def get_retracted_article_ids():
    """
    Return a list of Pubmed ids that are retracted
    """
    return json.loads(requests.get(pubmed_search).content)['esearchresult']['idlist']

def get_pubmed_detail(pubmed_id):
    """
    Use the Pubmed API to return the details of a pubmed article
    """
    return json.loads(requests.get(pubmed_deets+pubmed_id).content)['result'][pubmed_id]

def get_scholar_result(deets):
    """
    Given an article title, parse the google scholar results to generate metadata
    """
    words = deets['title'] + ' author:' + deets['sortfirstauthor']
    print words 
    query = SearchScholarQuery()
    query.set_words(words)
    querier = ScholarQuerier()
    try:
        querier.send_query(query)
    except (requests.exceptions.ConnectionError,
            requests.exceptions.ChunkedEncodingError,
            requests.exceptions.ReadTimeout):
        querier.send_query(query)

    if len(querier.articles) == 0:
        raise NoResultsError()
    
    if len(querier.articles) > 2:
        print len(querier.articles), 'results'
        raise TooManyResultsError()
    
    return querier.articles[0].attrs
    
def get_article_deets(pubmed_id):
    deets = get_pubmed_detail(pubmed_id)
    scholar = get_scholar_result(deets)
    article = dict(pubmed_deets=deets, pubmedid=pubmed_id, scholar_deets=scholar)

    return article

def count_number_of_citations(articles):
    total = 0
    for article in articles.values():
        total += article['scholar_deets']['num_citations'][0]
    return total

def main():
    retracted_articles = load_retracted_articles()
    article_ids = get_retracted_article_ids()
    random.shuffle(article_ids)
    try:
        for pubmed_id in article_ids:
            if pubmed_id not in retracted_articles:
                try:
                    retracted_articles[pubmed_id] = get_article_deets(pubmed_id)
                except TooManyResultsError:
                    print 'Too many results', pubmed_id
                    continue
                except NoResultsError:
                    print 'No results ?'
                    continue
                except NotATwoHundredError:
                    print 'We are being blocked!', pubmed_id
                    break
                except CaptchaError:
                    print 'Captcha detected in Google response'
                    print 'Time to switch proxies!'
                    break
                
            else:
                print 'Already have', pubmed_id
    finally:
        save_retracted_articles(retracted_articles)
        num_citations = count_number_of_citations(retracted_articles)
        print 'Retrieved', len(retracted_articles.keys()), '/', len(article_ids)
    return 0

if __name__ == '__main__':
    sys.exit(main())
