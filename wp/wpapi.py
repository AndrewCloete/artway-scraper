from __future__ import annotations
import json

from dataclasses import dataclass


@dataclass
class Config:
    base_url: str
    auth: tuple[str, str]

    @staticmethod
    def get_config() -> Config:
        with open(".env.json", "r") as f:
            env = json.load(f)
        return Config(base_url=env["url"], auth=(env["user"], env["psw"]))

    def url(self, path: str) -> str:
        return self.base_url + "/wp-json/wp/v2/" + path


# def create_post(entry):
#     content_dir = get_params_dir(entry)
#     with open(f"{content_dir}/content.html", "r") as f:
#         post_content = f.read()
#
#     entry_id = entry["id"]
#     parent_title = "no_parent"
#     if "parent" in entry:
#         parent_id = entry["parent"]
#         parent = visited.get(parent_id)
#         parent_title = parent["title"] if parent else "no_parent"
#
#     meta = {
#         "id": entry_id,
#         "parent": parent_title,
#     }
#
#     payload = {
#         "title": entry["title"],
#         "date": "2021-01-01T00:00:00",
#         "slug": entry_id,
#         "status": "draft",
#         "author": 1,
#         "format": "standard",
#         "content": post_content,
#         "meta": meta,
#     }
#
#     get_url = url + f"?search={entry['title']}"
#     print(get_url)
#     existing = requests.get(get_url, auth=(username, password))
#     print(existing.text)
#
#     response = requests.post(url, auth=(username, password), json=payload)
#     print(response.text)
#
#
# for entry in visited.values():
#     print(entry["title"])
#     if entry["action"] == "list":
#         if "location" in entry and entry["location"] == "subnav":
#             print("Creating category")
#             # create_category(entry)
#         print("skipping list")
#         continue
#
#     create_post(entry)
#     time.sleep(1)
