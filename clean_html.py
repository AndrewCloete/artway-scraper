from operator import itemgetter
from ParamsIndexRepo import (
    ParamsIndexRepo,
    BASE_DIR,
    get_html_path,
    get_html_path_named,
    AW_URL,
)
from bs4 import BeautifulSoup


visited = ParamsIndexRepo(BASE_DIR, "visited.json")

posts = visited.values()


def clean_html(post):
    id, title = itemgetter("id", "title")(post)
    path_original = get_html_path(id, title)
    with open(path_original, "r") as f:
        content = f.read()

    soup = BeautifulSoup(content, "html.parser")
    inner_f = soup.find_all("div", {"class": "art_threethird"})
    if len(inner_f) > 1:
        raise Exception("more than one art_threethird")
    if len(inner_f) < 1:
        raise Exception("less than one art_threethird")
    inner = inner_f[0]

    images = inner.find_all("img")
    for img in images:
        if "http" not in img["src"]:
            img["src"] = AW_URL + img["src"]

    del_tags = ["style", "class", "xmlns"]
    tags = inner.find_all()
    for tag in tags:
        for dt in del_tags:
            if tag.has_attr(dt):
                del tag.attrs[dt]

    anchors = inner.find_all("a")
    for a in anchors:
        if a["href"].startswith("?"):
            a.decompose()

    for unwrap in ["h1", "p", "strong"]:
        for u in inner.find_all(unwrap):
            u.unwrap()

    # Does not look so good
    # spans = inner.find_all("span")
    # for span in spans:
    #     if span.get_text() == " ":
    #         span.decompose()

    # print(inner.prettify())

    path_clean = get_html_path_named(id, title, "clean")
    with open(path_clean, "w") as f:
        f.write(str(inner))
        # content = f.read()

    print(f"vim -d '{path_original}' '{path_clean}'")
    print(f"open '{path_original}' && open '{path_clean}'")
    print()

    # for idx, url in enumerate(post["image_urls"]):
    # print(url)vim -d '/Users/user/Workspace/artway-scraper/data/content/881_C jaar, Pasen 2 - De droom van Jakob van Chagall/original.html' '/Users/user/Workspace/artway-scraper/data/content/881_C jaar, Pasen 2 - De droom van Jakob van Chagall/clean.html'


for post in posts[1020:1040]:
    clean_html(post)
