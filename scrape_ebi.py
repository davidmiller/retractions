"""
Check for the most-cited retracted pubmed ids according to ebi
"""
import json

import requests

from scrape_articles import get_retracted_article_ids, get_pubmed_detail

base_url = 'http://www.ebi.ac.uk/europepmc/webservices/rest/MED/{0}/citations/1/json'
base_url = 'http://www.ebi.ac.uk/europepmc/webservices/rest/search/query=ext_id:{0}%20src:med&format=json'

ids = get_retracted_article_ids()
retracted = []
for i, pubmedid in enumerate(ids):
    detail = get_pubmed_detail(pubmedid)
    title = detail['title']
    print i, title
    resp = requests.get(base_url.format(pubmedid))
    citations = json.loads(resp.content)['resultList']['result'][0]['citedByCount']
    print citations, 'citations'
    retracted.append((citations, title, 'http://www.ncbi.nlm.nih.gov/pubmed/'+pubmedid, detail))

sorted_citations = sorted(retracted)
sorted_citations.reverse()

for a in sorted_citations[:5]:
    print a[0], a[1]

with open('ebi.json', 'w') as fh:
    fh.write(json.dumps(sorted_citations, indent=2))
