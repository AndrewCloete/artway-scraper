"""
python3 -m venv env
"""

import requests
import html2text
from bs4 import BeautifulSoup
import pandas as pd

BASE_URL = 'https://artway.eu/content.php'

SEED_PARAMS = [ {'title': 'Articles', 'id': '74', 'action': 'show', 'lang': 'en'}, ]
visited = {}
seen = {}

def url(params):
    paramsStr = '&'.join([f'{k}={v}' for k, v in params.items()])
    return BASE_URL + '?' + paramsStr

def extract_query_params(params):
    paramsList = params.replace("?", "").split('&')
    return {p.split('=')[0]: p.split('=')[1] for p in paramsList}

def get_links(params, query, location):
    parent_id = params['id']
    page = requests.get(url(params))
    soup = BeautifulSoup(page.text, 'html.parser')
    content = soup.find_all(query['tag'], query['attrs'])
    anchors = content[0].find_all('a')
    return [{"title": a.contents[0].strip(), 'location': location, 'parent': parent_id,  **extract_query_params(a['href'])} for a in anchors]

def get_subnav_links(params):
    return get_links(params, {'tag': 'ul', 'attrs': {'class':'subnav options'}}, 'subnav')

def get_content_links(params):
    return get_links(params, {'tag': 'div', 'attrs': {'id':'contentmain'}}, 'content')

def push_visited(params):
    for param in params:
        visited[param['id']] = param

def push_seen(params):
    for param in params:
        seen[param['id']] = param

def unvisited():
    return [v for v in visited.values() if v['id'] not in seen]


articles_subnav = get_subnav_links(SEED_PARAMS[0])
push_visited(SEED_PARAMS)

for nav in articles_subnav:
    if nav['id'] in visited:
        continue
    push_visited([nav])
    print("Visiting: ", nav['title'])
    sub_aritcles = get_content_links(nav)
    push_visited(sub_aritcles) # not really visited but just for show

    print("Found: ", len(sub_aritcles), " articles")

df = pd.DataFrame(visited.values())
df.to_csv('/tmp/artway_index.csv', index=False)


