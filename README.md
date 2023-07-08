This tool aims to scrape ArtWay.eu to automate as far possible migrating the content to a new platform.

# Getting started
Restore dependencies
```sh
python3 -m venv env
activate
pip install -r requirements.txt
```

Scrape to index site
```sh
python scrape.py
```

Write the index to csv for easy viewing
```sh
python stats.py
```
