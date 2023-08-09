import requests
import time
from ParamsIndexRepo import ParamsIndexRepo, BASE_DIR, get_params_dir

# Reference: https://developer.wordpress.org/rest-api/reference/posts/
BASE_URL = "https://2r095.wpdevsite.co"

username = "andrew"
password = "xTwH tN0f bQHv E8cD 61mx kcZn"
url = BASE_URL + "/wp-json/wp/v2/posts"

# response = requests.get(url, auth=(username, password))
# print(response.text)

visited = ParamsIndexRepo(BASE_DIR, "visited.json")


def create_category(entry):
    payload = {
        "name": entry["title"],
    }
    response = requests.post(
        BASE_URL + "/wp-json/wp/v2/categories",
        auth=(username, password),
        json=payload,
    )
    print(response.text)


def create_post(entry):
    content_dir = get_params_dir(entry)
    with open(f"{content_dir}/content.html", "r") as f:
        post_content = f.read()

    entry_id = entry["id"]
    parent_title = "no_parent"
    if "parent" in entry:
        parent_id = entry["parent"]
        parent = visited.get(parent_id)
        parent_title = parent["title"] if parent else "no_parent"

    meta = {
        "id": entry_id,
        "parent": parent_title,
    }

    payload = {
        "title": entry["title"],
        "date": "2021-01-01T00:00:00",
        "slug": entry_id,
        "status": "draft",
        "author": 1,
        "format": "standard",
        "content": post_content,
        "meta": meta,
    }

    get_url = url + f"?search={entry['title']}"
    print(get_url)
    existing = requests.get(get_url, auth=(username, password))
    print(existing.text)

    response = requests.post(url, auth=(username, password), json=payload)
    print(response.text)


for entry in visited.values():
    print(entry["title"])
    if entry["action"] == "list":
        if "location" in entry and entry["location"] == "subnav":
            print("Creating category")
            create_category(entry)
        print("skipping list")
        continue

    # create_post(entry)
    # time.sleep(1)
