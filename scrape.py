from pathlib import Path

import requests
from bs4 import BeautifulSoup
import html2text

import lib

from ParamsIndexRepo import ParamsIndexRepo, BASE_DIR, get_params_dir

BASE_URL = "https://artway.eu/content.php"

SEED_PARAMS = [
    {
        "title": "Articles",
        "id": "74",
        "action": "show",
        "lang": "en",
        "p_id": "0",
        "href_path": "id=74&action=show&lang=en",
    },
    {
        "title": "Artikelen",
        "id": "74",
        "lang": "nl",
        "action": "show",
        "p_id": "0",
        "href_path": "id=74&action=show&lang=nl",
    },
    {
        "title": "Articles - Deutsche Artikel",
        "id": "64",
        "lang": "en",
        "p_id": "0",
        "href_path": "id=64&lang=en",
    },
    {
        "title": "Articles - Articles francais",
        "id": "94",
        "lang": "en",
        "p_id": "0",
        "href_path": "id=94&lang=en",
    },
    {
        "title": "Articles - Portuguese",
        "id": "98",
        "lang": "en",
        "p_id": "0",
        "href_path": "id=98&lang=en",
    },
    {
        "title": "Art and the Church",
        "id": "4",
        "action": "show",
        "lang": "en",
        "p_id": "0",
        "href_path": "id=4&lang=en&action=show",
    },
    {
        "title": "Kerk & kunst",
        "id": "4",
        "action": "show",
        "lang": "nl",
        "p_id": "0",
        "href_path": "id=4&lang=nl&action=show",
    },
    {
        "title": "Travel tips",
        "id": "6",
        "action": "show",
        "lang": "en",
        "p_id": "0",
        "href_path": "id=6&lang=en&action=show",
    },
    {
        "title": "Reistips",
        "id": "6",
        "action": "show",
        "lang": "nl",
        "p_id": "0",
        "href_path": "id=6&lang=nl&action=show",
    },
    {
        "title": "Artists",
        "id": "1",
        "action": "show",
        "lang": "en",
        "p_id": "0",
        "href_path": "id=1&action=show&lang=en",
    },
    {
        "title": "Kunstenaars",
        "id": "1",
        "action": "show",
        "lang": "nl",
        "p_id": "0",
        "href_path": "id=1&action=show&lang=nl",
    },
]


visited = ParamsIndexRepo(BASE_DIR, "visited.json")
seen = ParamsIndexRepo(BASE_DIR, "seen.json")


def url(params):
    # paramsStr = "&".join(
    #     [f"{k}={v}" for k, v in params.items() if not k.startswith("p_")]
    # )
    return BASE_URL + "?" + params["href_path"]


def extract_query_params(href):
    href_path = href.split("?")[1]
    if href_path[-1] == "&":
        href_path = href_path[:-1]
    paramsList = href_path.split("&")
    params = {p.split("=")[0]: p.split("=")[1] for p in paramsList}
    params["href_path"] = href_path
    return params


def unvisited():
    # Sort to promote a breadth-first search
    return sorted(
        [s for s in seen.values() if not visited.contains(s)],
        key=lambda s: int(s["id"]),
    )


def get_links(page_soup, params, query, location):
    not_pass_thru = [
        "lang",
        "title",
        "href_path",
        "p_id",
        "p_action",
        "p_location",
        "p_type",
    ]
    parent_params = {f"p_{k}": v for k, v in params.items() if k not in not_pass_thru}
    content = page_soup.find_all(query["tag"], query["attrs"])
    anchors = content[0].find_all("a")
    result = []
    for a in anchors:
        full_title_string = a.get_text().encode('utf-8').decode('utf-8') if a.contents else "UNKNOWN"
        full_title_string = full_title_string.strip()
        parsed_title = lib.best_effort_title_parse(full_title_string)
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

    content_length = len(raw_content)
    content_dir = get_params_dir(params)
    content_dir.mkdir(parents=True, exist_ok=True)
    # Persist content
    with open(content_dir / "original.html", "w") as f:
        f.write(raw_content)
    with open(content_dir / "markdown.md", "w") as f:
        f.write(markdown_content)

    return {"image_urls": image_urls, "length": content_length}


def get_page_links(params):
    if visited.contains(params):
        return
    print("Visiting: ", params["id"], params["title"])
    page = requests.get(url(params))
    page_soup = BeautifulSoup(page.content, "html.parser")
    seen.pushOne(params)
    subnav_links = get_subnav_links(page_soup, params)
    seen.pushMany(subnav_links)
    if "action" not in params or params["action"] == "list":
        content_links = get_content_links(page_soup, params)
        print("Found: ", len(content_links), " articles")
        seen.pushMany(content_links)

    content_stats = get_content(params, page_soup)
    params = {**params, **content_stats}
    visited.pushOne(params)


Path(BASE_DIR).mkdir(parents=True, exist_ok=True)

seen.pushMany(SEED_PARAMS)

for i in range(0, 7):
    print("Iteration: ", i)
    for params in unvisited():
        get_page_links(params)
