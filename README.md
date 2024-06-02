This tool aims to scrape ArtWay.eu to automate as far possible migrating the content to a new platform.

# Getting started
Restore dependencies
```sh
python3 -m venv env
activate
pip install -r requirements.txt
```


```sh
python scrape.py

# Taxonomies
python stats.py
python taxonomy2.py

# Content
python master_lables.py
python clean_html.py
python wpallimport.py
```

