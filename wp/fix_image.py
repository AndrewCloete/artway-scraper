import json
from wpapi import Config
from bs4 import BeautifulSoup
import requests

cnf = Config.get_config()

with open("/tmp/articles.json", "r") as f:
    articles_json = json.load(f)

for art in articles_json:
    id = art["id"]
    content = art["content"]["rendered"]
    title = art["title"]["rendered"]

    soup = BeautifulSoup(content, "html.parser")
    images = soup.find_all("img")
    for img in images:
        img["src"] = (
            img["src"]
            .replace(" ", "-")
            .replace("(", "")
            .replace(")", "")
            .replace("JPG", "jpg")
            .replace("PNG", "png")
        )

    fixed_content = str(soup)
    # print(fixed_content)

    response = requests.put(
        cnf.url("article") + f"/{id}",
        auth=cnf.auth,
        headers={"Content-Type": "application/json"},
        json={"title": title, "content": fixed_content},
    )
    print(json.dumps(response.json(), indent=2))
