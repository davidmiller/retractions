import sys
import time
import requests 
import json

from scholar import ScholarQuerier, SearchScholarQuery, csv, ScholarConf

pubmed_search = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&retmax=10000&term=%22retracted%20publication%22[Publication%20Type]'

base_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&rettype=abstract&id='

ids = json.loads(requests.get(pubmed_search).content)['esearchresult']['idlist']

total_silly_citations = 0
retracted_papers = []

ScholarConf.COOKIE_JAR_FILE = 'cookies.txt'
ScholarConf.LOG_LEVEL = 4

for i, pubmedid in enumerate(ids):
    if i % 10 == 0:
        if i > 0:
            print 'sleeping for 4'
            time.sleep(4)

    
    pubmedid = pubmedid.strip()

    result = json.loads(requests.get(base_url+pubmedid).content)['result'][pubmedid]['title']

    result = 'Open source, open standards, and health care information systems.'
    print result
    
    query = SearchScholarQuery()
    query.set_words(result)

    querier = ScholarQuerier()
    querier.send_query(query)

    if len(querier.articles) == 0:
        print 'No Articles :('
        # continue
        break

    if len(querier.articles) > 1:
        print 'Too Many articles'
        # break
        continue

    num_citations = querier.articles[0].attrs['num_citations'][0]

    print num_citations

    total_silly_citations += num_citations

    print 'Total silly citations =', total_silly_citations
    retracted_papers.append(dict(title=result, pubmedid=pubmedid, citations=num_citations))

    break


with open('retracted.citations.json', 'w') as fh:
    fh.write(json.dumps(retracted_papers, indent=2))
