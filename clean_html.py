import re
from operator import itemgetter
from ParamsIndexRepo import (
    ParamsIndexRepo,
    BASE_DIR,
    get_html_path,
    get_html_path_named,
    get_flags_path,
    AW_URL,
)
from bs4 import BeautifulSoup, Tag
import pandas as pd


visited = ParamsIndexRepo(BASE_DIR, "visited.json")

posts = visited.unique_href_values()


def remove_empty_elements_recur(soup):
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
        remove_empty_elements_recur(soup)


# Decompose the completely empty elements, but only unwrap the elements with blank chars
def remove_empty_elements(soup):
    elements = soup.find_all(["span", "div"])

    # Identify empty elements
    for element in elements:
        if not element.contents:
            element.decompose()

    elements = soup.find_all(["span", "strong"])
    for element in elements:
        if not element.text.strip():
            element.unwrap()


def clean_html(post):
    id, title = itemgetter("id", "title")(post)
    lang = post["lang"] if "lang" in post else "none"
    action = post["action"] if "action" in post else "none"
    flag = {"id": id, "lang": lang, "action": action}
    path_original = get_html_path(id, lang, title)
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

    # Remove titles
    h1s = soup.select("h1")
    if len(h1s) > 0:
        flag["deleted_title"] = str(h1s[0].get_text())
        h1s[0].decompose()

    # Replace each <b> tag with <strong> tag
    for b in inner.find_all("b"):
        b.name = "strong"

    def find_innermost_text(element) -> str:
        if element.string:
            return element.string
        for child in element.children:
            result = find_innermost_text(child)
            if result:
                return result
        return ""

    # Best effort infer subtitle and author
    pattern = re.compile(r"^\b(by|door|durch|par)\s{0,5}[A-Z]")
    strongs = inner.find_all("strong")
    for s in strongs:
        txt = find_innermost_text(s)
        if len(txt) < 50 and pattern.search(txt):
            flag["deleted_author"] = str(txt) + ""
            s.decompose()
            # print(id, lang, action, flag["deleted_author"])

    # Add HTTP URL to images
    images = inner.find_all("img")
    for img in images:
        if "http" not in img["src"]:
            img["src"] = AW_URL + img["src"]
            img["src"] = img["src"].replace(" ", "%20")

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

    # Remove anchor tags starting with "?". This remove the top link
    anchors = inner.find_all("a")
    for a in anchors:
        if a.has_attr("href") and a["href"].startswith("?"):
            a.decompose()  # Remove the tag from the document

    # horz_rule = inner.find(
    #     ["div", "span", "strong", "p"], class_=re.compile("\\*\\*\\*\\*")
    # )
    horz_rule = inner.find(string=re.compile(r"\*\*\*\*"))
    if horz_rule:
        print("Found rule!!! " + id)
        horz_rule.replace_with(soup.new_tag("hr"))
        flag["hr"] = True

    # for unwrap in ["h1", "p"]:
    #     for u in inner.find_all(unwrap):
    #         u.unwrap()

    # Does not look so good
    # spans = inner.find_all("span")
    # for span in spans:
    #     if span.get_text() == " ":
    #         span.decompose()

    # print(inner.prettify())

    for _ in range(10):
        remove_empty_elements(inner)

    # Post HTML cleaning
    inner_str = str(inner)
    if "->" in inner_str:
        print("FOUND -> " + id)
    if "-&gt;" in inner_str:
        print("FOUND -&gt; " + id)
    inner_str = inner_str.replace("->", "")
    inner_str = inner_str.replace("-&gt;", "")

    path_clean = get_html_path_named(id, lang, title, "clean")
    with open(path_clean, "w") as f:
        f.write(inner_str)
    # content = f.read()

    # print(f"code -d '{path_original}' '{path_clean}'")
    # print(f"open '{path_original}' && open '{path_clean}'")

    # for idx, url in enumerate(post["image_urls"]):
    # print(url)vim -d '/Users/user/Workspace/artway-scraper/data/content/881_C jaar, Pasen 2 - De droom van Jakob van Chagall/original.html' '/Users/user/Workspace/artway-scraper/data/content/881_C jaar, Pasen 2 - De droom van Jakob van Chagall/clean.html'
    return flag


flags = []
# for post in posts[500:700]:
# for post in posts[1020:1021]:
for post in posts:
    flag = clean_html(post)
    flags.append(flag)

df_flags = pd.DataFrame(flags).astype({"id": "int64"})
df_flags.to_csv(get_flags_path(), index=False)

df_flags = pd.DataFrame(flags).astype({"id": "int64"}).set_index(["id", "lang"])
# df_human = get_df_human()
# df = df_human.merge(df_flags, how="inner")
# df = df.drop_duplicates(subset="link", keep="last")
#
# # post types: article, interview, vm, list of posts, book review
# extra_cols = (
#     "date",
#     "artwork_name",
#     "subtitle",
#     "author_bio",
# )
# for col in extra_cols:
#     df[col] = None


# df.to_csv(get_flags_path(), index=False)
