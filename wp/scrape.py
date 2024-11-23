import json
from wpapi import Config
import requests

cnf = Config.get_config()


def get_media():
    response = requests.get(cnf.url("media"), auth=cnf.auth)
    print(json.dumps(response.json(), indent=2))


def get_articles():
    response = requests.get(cnf.url("article"), auth=cnf.auth)
    with open("/tmp/articles.json", "w") as f:
        json.dump(response.json(), f, indent=2)


get_articles()
