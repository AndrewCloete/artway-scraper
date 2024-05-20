from operator import itemgetter
from ParamsIndexRepo import (
    ParamsIndexRepo,
    BASE_DIR,
    get_html_path,
    get_html_path_named,
    get_flags_path,
    AW_URL,
    get_master_sheet_path,
)
from bs4 import BeautifulSoup, Tag
import pandas as pd


visited = ParamsIndexRepo(BASE_DIR, "visited.json")

posts = visited.unique_href_values()


def remove_empty_elements(soup):
    # Find all <span> and <div> elements
    elements = soup.find_all(["span", "div"])
    empty_elements = []

    # Identify empty elements
    for element in elements:
        # Check if the element is empty or contains only whitespace
        if not element.text.strip() and not element.contents:
            empty_elements.append(element)
        elif not element.text.strip() and all(
            child in empty_elements
            for child in element.contents
            if isinstance(child, Tag)
        ):
            empty_elements.append(element)

    # If we have empty elements, decompose them
    if empty_elements:
        for element in empty_elements:
            element.decompose()
        # Recursively call the function to check again
        remove_empty_elements(soup)


def clean_html(post):
    id, title = itemgetter("id", "title")(post)
    flag = {"id": id}
    path_original = get_html_path(id, title)
    with open(path_original, "r") as f:
        content = f.read()

    soup = BeautifulSoup(content, "html.parser")
    html_string = str(soup)
    cleaned_html = html_string.replace("&nbsp;", "")
    soup = BeautifulSoup(cleaned_html, "html.parser")

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

    remove_empty_elements(soup)

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


df_master = pd.read_csv(get_master_sheet_path())
df_flags = pd.DataFrame(flags)
df_master = df_master.astype({"id": "int64"})
df_flags = df_flags.astype({"id": "int64"})


df = df_master.merge(df_flags, on="id", how="inner")
df = df.drop_duplicates(subset="link", keep="last")

df.to_csv(get_flags_path(), index=False)
