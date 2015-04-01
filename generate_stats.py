"""
Generate headline stats for our scraped retracted articles
"""
import json

from scrape_articles import load_retracted_articles

articles = load_retracted_articles()

highest = 0

citations = []

for article in articles.values():
    title = article['pubmed_deets']['title']
    num_citations = article['scholar_deets']['num_citations'][0]
    citations.append((num_citations, title))
    
sorted_citations = sorted(citations)
sorted_citations.reverse()
for a in sorted_citations[:5]:
    print a[0], a[1]
