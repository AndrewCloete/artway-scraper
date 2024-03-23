import copy
import pandas as pd
from ParamsIndexRepo import ParamsIndexRepo, AW_URL, BASE_DIR, get_params_dir

visited = ParamsIndexRepo(BASE_DIR, "visited.json")

posts = visited.values()


def match_filter(key, value):
    def f(rec):
        return key in rec and rec[key] == value

    return f


def post_filter(rec):
    if "lang" not in rec or rec["lang"] != "en":
        return False
    if "action" not in rec or rec["action"] != "show":
        return False
    # if int(rec["id"]) < 200 or int(rec["id"]) > 900:
    #     return False
    if "image_urls" not in rec or len(rec["image_urls"]) < 1:
        return False
    return True


posts = filter(post_filter, posts)

clean_posts = []
for post in posts:
    p = copy.deepcopy(post)
    p["image_urls"] = [
        url if url.startswith("http") else AW_URL + url for url in p["image_urls"]
    ]
    clean_posts.append(p)


wpall_posts = []
for post in clean_posts:
    p = {}
    p["lang"] = post["lang"]
    p["common_id"] = post["id"]
    p["title"] = post["title"]

    with open(
        f"{BASE_DIR}/content/{post['id']}_{post['title']}/original.html", "r"
    ) as f:
        content = f.read()
        p["body_text"] = content

    for idx, url in enumerate(post["image_urls"]):
        p[f"image_{idx}"] = url

    wpall_posts.append(p)


df = pd.DataFrame(wpall_posts)

df.to_csv("/tmp/wpall_import.csv", na_rep="")
