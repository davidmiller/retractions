"""
Check for the most-cited retracted pubmed ids according to ebi
"""
import json

from lxml import html
import requests

from scrape_articles import get_retracted_article_ids, get_pubmed_detail

base_url = 'http://scholar.google.com/scholar?cites=http://www.ncbi.nlm.nih.gov/pubmed/{0}'

def extract_num_citations(markup):
    tree = html.fromstring(markup)
    div = tree.cssselect('#gs_ab_md')[0]
    return int(div.text_content().split()[0])
    
ids = get_retracted_article_ids()
retracted = []
for i, pubmedid in enumerate(ids):
    detail = get_pubmed_detail(pubmedid)
    title = detail['title']
    print i, title
    resp = requests.get(base_url.format(pubmedid))
    if resp.status_code != 200:
        raise Exception('Google Say Go Away Please')
    citations = extract_num_citations(resp.content)
    print citations, 'citations'
    retracted.append((len(citations), title))

sorted_citations = sorted(retracted)
sorted_citations.reverse()

for a in sorted_citations[:5]:
    print a[0], a[1]
