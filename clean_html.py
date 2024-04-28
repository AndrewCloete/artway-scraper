from operator import itemgetter
from ParamsIndexRepo import (
    ParamsIndexRepo,
    BASE_DIR,
    get_html_path,
    get_html_path_named,
    get_flags_path,
    AW_URL,
)
from bs4 import BeautifulSoup
import pandas as pd


visited = ParamsIndexRepo(BASE_DIR, "visited.json")

posts = visited.values()


def clean_html(post):
    id, title, href_path = itemgetter("id", "title", "href_path")(post)
    flag = {"id": id, "href": f"{AW_URL}/content.php?{href_path}", "title": title}
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
    del inner["class"]

    h1_anchor = soup.select('a[href*="id="]')
    for a in h1_anchor:
        a.decompose()

    # Replace each <b> tag with <strong> tag
    for b in inner.find_all("b"):
        b.replace_with(soup.new_tag("strong", **b.attrs))

    # Best effort infer subtitle and author
    strong = inner.find_all("strong")
    if len(strong) > 1:
        flag["strong0"] = strong[0].text
        flag["strong1"] = strong[1].text

    images = inner.find_all("img")
    for img in images:
        if "http" not in img["src"]:
            img["src"] = AW_URL + img["src"]

    # Table images
    tables = inner.find_all("table")
    flag["table_len"] = len(tables)
    max_table_image_count = 0
    for table in tables:
        table_images = table.find_all("img")
        len_table_images = len(table_images)
        if len_table_images > max_table_image_count:
            max_table_image_count = len_table_images

        if len_table_images == 1:
            table.replace_with(table_images[0])
    flag["max_table_image_count"] = max_table_image_count

    del_tags = ["style", "class", "xmlns"]
    tags = inner.find_all()
    for tag in tags:
        for dt in del_tags:
            if tag.has_attr(dt):
                del tag.attrs[dt]

    anchors = inner.find_all("a")
    for a in anchors:
        if "href" not in a:
            continue
        if a["href"].startswith("?"):
            a.decompose()

    for unwrap in ["h1", "p"]:
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

    # print(f"code -d '{path_original}' '{path_clean}'")
    # print(f"open '{path_original}' && open '{path_clean}'")

    # for idx, url in enumerate(post["image_urls"]):
    # print(url)vim -d '/Users/user/Workspace/artway-scraper/data/content/881_C jaar, Pasen 2 - De droom van Jakob van Chagall/original.html' '/Users/user/Workspace/artway-scraper/data/content/881_C jaar, Pasen 2 - De droom van Jakob van Chagall/clean.html'
    return flag


flags = []
for post in posts:  # [1020:1040]:
    flag = clean_html(post)
    flags.append(flag)

    df = pd.DataFrame(flags).to_csv(get_flags_path())
