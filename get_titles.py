"""
Scrape and store citations of retracted pubmed papers.
"""
import sys
import time
import requests 
import json

from scholar import ScholarQuerier, SearchScholarQuery, csv, ScholarConf, NotATwoHundredError

pubmed_search = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&retmax=10000&term=%22retracted%20publication%22[Publication%20Type]'
pubmed_deets = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&rettype=abstract&id='


ScholarConf.LOG_LEVEL = 4

class Error(Exception): pass
class WrongNumberOfResultsError(Error): pass

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

def get_scholar_result(title):
    """
    Given an article title, parse the google scholar results to generate metadata
    """
    query = SearchScholarQuery()
    query.set_words(title)
    querier = ScholarQuerier()
    querier.send_query(query)

    if len(querier.articles) == 0:
        raise WrongNumberOfResultsError()
    
    if len(querier.articles) > 1:
        raise WrongNumberOfResultsError()
    
    return querier.articles[0].attrs
    
def get_article_deets(pubmed_id):
    deets = get_pubmed_detail(pubmed_id)
    print deets ['title']
    scholar = get_scholar_result(deets['title'])
    article = dict(pubmed_deets=deets, pubmedid=pubmed_id, scholar_deets=scholar)

    return article

def count_number_of_citations(articles):
    total = 0
    for article in articles.values():
        total += article['scholar_deets']['num_citations'][0]
    return total

def main():
    retracted_articles = load_retracted_articles()

    try:
        for pubmed_id in get_retracted_article_ids():
            if pubmed_id not in retracted_articles:
                try:
                    retracted_articles[pubmed_id] = get_article_deets(pubmed_id)
                except WrongNumberOfResultsError:
                    print 'Wrong number of results', pubmed_id
                    continue
                except NotATwoHundredError:
                    print 'We are being blocked!', pubmed_id
                    break
    finally:
        save_retracted_articles(retracted_articles)
        num_citations = count_number_of_citations(retracted_articles)
        print 'Silly citation count =', num_citations
    return 0

if __name__ == '__main__':
    sys.exit(main())



with open('retracted.citations.json', 'w') as fh:
    fh.write(json.dumps(retracted_papers, indent=2))
