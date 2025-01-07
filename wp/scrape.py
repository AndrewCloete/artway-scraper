import json
from wpapi import Config
import requests

cnf = Config.get_config()


def get_articles():
    response = requests.get(cnf.url("article") + "/17063", auth=cnf.auth)
    with open("/tmp/articles.json", "w") as f:
        json.dump(response.json(), f, indent=2)


get_articles()
