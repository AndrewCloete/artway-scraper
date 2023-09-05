from pathlib import Path

import requests
from bs4 import BeautifulSoup
import html2text
import markdown

import lib

from ParamsIndexRepo import ParamsIndexRepo, BASE_DIR, get_params_dir

BASE_URL = "https://artway.eu/content.php"

SEED_PARAMS = [
    {"title": "Artists", "id": "1", "action": "show", "lang": "en", "p_id": "0"},
    {"title": "Articles", "id": "74", "action": "show", "lang": "en", "p_id": "0"},
    {
        "title": "Art and the Church",
        "id": "4",
        "action": "show",
        "lang": "en",
        "p_id": "0",
    },
]


visited = ParamsIndexRepo(BASE_DIR, "visited.json")
seen = ParamsIndexRepo(BASE_DIR, "seen.json")


def url(params):
    paramsStr = "&".join(
        [f"{k}={v}" for k, v in params.items() if not k.startswith("p_")]
    )
    return BASE_URL + "?" + paramsStr


def extract_query_params(href):
    params = href.split("?")[1]
    if params[-1] == "&":
        params = params[:-1]
    paramsList = params.split("&")
    return {p.split("=")[0]: p.split("=")[1] for p in paramsList}


def unvisited():
    return [s for s in seen.values() if not visited.contains(s)]


def get_links(page_soup, params, query, location):
    not_pass_thru = ["action", "lang", "location"]
    parent_params = {f"p_{k}": v for k, v in params.items() if k not in not_pass_thru}
    content = page_soup.find_all(query["tag"], query["attrs"])
    anchors = content[0].find_all("a")
    result = []
    for a in anchors:
        full_title_string = a.get_text() if a.contents else "UNKNOWN"
        full_title_string = full_title_string.strip()
        parsed_title = lib.best_effort_title_parse(full_title_string)
        # title = bytes(title, 'unicode_escape').decode('unicode_escape', 'ignore').strip()
        params = extract_query_params(a["href"])
        result.append({**parsed_title, "location": location, **parent_params, **params})
    return result


def get_subnav_links(page_soup, params):
    return get_links(
        page_soup, params, {"tag": "ul", "attrs": {"class": "subnav options"}}, "subnav"
    )


def get_content_links(page_soup, params):
    return get_links(
        page_soup, params, {"tag": "div", "attrs": {"id": "contentmain"}}, "content"
    )


def get_content(params, page_soup):
    content = page_soup.find_all("div", {"id": "contentmain"})
    image_urls = [img["src"] for img in content[0].find_all("img")]

    # Convert HTML to markdown and then back to HTML to keep only the essential structure
    raw_content = str(content[0])
    markdown_content = html2text.html2text(raw_content)
    rehidrated_html_content = markdown.markdown(markdown_content)

    content_length = len(rehidrated_html_content)
    content_dir = get_params_dir(params)
    content_dir.mkdir(parents=True, exist_ok=True)
    # Persist content
    with open(content_dir / "original.html", "w") as f:
        f.write(raw_content)
    with open(content_dir / "markdown.md", "w") as f:
        f.write(markdown_content)
    with open(content_dir / "content.html", "w") as f:
        f.write(rehidrated_html_content)

    return {"image_urls": image_urls, "length": content_length}


def get_page_links(params):
    if visited.contains(params):
        return
    print("Visiting: ", params["title"])
    page = requests.get(url(params))
    page.encoding = "unicode_escape"
    page_soup = BeautifulSoup(page.text, "html.parser")
    seen.pushOne(params)
    subnav_links = get_subnav_links(page_soup, params)
    seen.pushMany(subnav_links)
    if params["action"] == "list":
        content_links = get_content_links(page_soup, params)
        print("Found: ", len(content_links), " articles")
        seen.pushMany(content_links)

    content_stats = get_content(params, page_soup)
    params = {**params, **content_stats}
    visited.pushOne(params)


Path(BASE_DIR).mkdir(parents=True, exist_ok=True)

seen.pushMany(SEED_PARAMS)

for i in range(0, 5):
    print("Iteration: ", i)
    for params in unvisited():
        get_page_links(params)
