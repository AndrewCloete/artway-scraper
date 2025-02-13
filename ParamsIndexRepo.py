import ast
from pathlib import Path
import json

from urllib.parse import parse_qsl, urlencode
import pandas as pd

BASE_DIR = "/Users/user/Workspace/artway-scraper/data"
AW_URL = "https://www.artway.eu"


def get_params_dir(id, lang, title):
    return Path(BASE_DIR) / "content" / f"{id}_{lang}_{title}"


def get_html_path_named(id, lang, title, name):
    return get_params_dir(id, lang, title) / f"{name}.html"


def get_html_path(id, lang, title):
    return get_html_path_named(id, lang, title, "original")


def get_flags_path():
    return Path(BASE_DIR) / "flags.csv"


def get_taxonomies_path():
    return Path(BASE_DIR) / "taxonomies.csv"


def get_tags_path():
    return Path(BASE_DIR) / "tags.csv"


def get_tags_reference_path():
    return Path(BASE_DIR) / "tags_reference.csv"


def get_bibbook_reference_path():
    return Path(BASE_DIR) / "bib_books.csv"


def get_post_type_changes_path():
    return Path(BASE_DIR) / "post_type_changes.csv"


def get_seen_limit_path():
    return Path(BASE_DIR) / "seen_limit.csv"


def get_master_sheet_path():
    return Path(BASE_DIR) / "master_sheet.csv"


def get_human_sheet_path():
    return Path(BASE_DIR) / "human_sheet.csv"


def get_creator_path(origin: str, kind: str):
    return Path(BASE_DIR) / f"{origin}_{kind}.csv"


def get_creator_df(origin: str, kind: str):
    def parse_articles(article_str: str):
        if "[" not in article_str:
            return []
        articles = ast.literal_eval(article_str)
        return [int(x) for x in articles]

    return pd.read_csv(
        str(get_creator_path(origin, kind)),
        index_col=0,
        converters={"articles": parse_articles},
    )


def get_similars_path():
    return Path(BASE_DIR) / "similars.csv"


def get_filtered_similars_path():
    return Path(BASE_DIR) / "similars_filtered.csv"


def split_tags(x):
    if x != x:
        return []
    return x.split(",")


def get_df_tax():
    df = pd.read_csv(get_taxonomies_path())
    df["taxonomies"] = df["tags"].apply(split_tags)
    df["continent"] = df["p_continent"]
    df["country"] = df["p_country"]
    df["period"] = df["p_period"]
    df["char"] = df["p_char"]
    df["index"] = df.apply(lambda r: str(r["id"]) + "_" + r["lang"], axis=1)
    df = df.astype({"id": "int64"})[
        ["id", "lang", "index", "taxonomies", "continent", "country", "period", "char"]
    ]
    return df.set_index(["id", "lang"])


def get_df_flags():
    df = pd.read_csv(get_flags_path())
    df["index"] = df.apply(lambda r: str(r["id"]) + "_" + r["lang"], axis=1)
    df = df.astype({"id": "int64"})
    df.drop(["table_len", "max_table_image_count"], axis=1, inplace=True)
    return df.set_index(["id", "lang", "action"])


def get_df_human():
    df = pd.read_csv(get_human_sheet_path())
    df["action"] = df["post_type"].apply(
        lambda x: "list" if x == "list of posts" else "show"
    )
    df["real_lang"] = df["lang"]
    df["lang"] = df["lang"].apply(lambda lang: lang if lang in ["en", "nl"] else "en")
    df["index"] = df.apply(lambda r: str(r["id"]) + "_" + r["lang"], axis=1)
    not_found = df["comments"].apply(lambda c: "not found" in c if c == c else False)
    df = df[~not_found]
    df = df.astype({"id": "int64"})
    return df.set_index(["id", "lang", "action"])


def get_wpallimport_cache_path(html_select):
    return Path(BASE_DIR) / f"wpall_import_{html_select}_cache.csv"


def get_wpallimport_path(html_select):
    return Path(BASE_DIR) / f"wpall_import_{html_select}.csv"


def get_wpallimport_xlsx(html_select):
    return Path(BASE_DIR) / f"wpall_import_{html_select}.xlsx"


def normalize_qparams(qparams):
    sorted_params = sorted(parse_qsl(qparams))
    return urlencode(sorted_params)


def filter_unique_hrefs(entries):
    seen = {}
    for entry in entries:
        value = entry["href_path"]
        if value not in seen:
            seen[value] = entry
    return list(seen.values())


class ParamsIndexRepo:
    def __init__(self, base_dir, filename):
        self.base_dir = base_dir
        self.filename = filename
        self.path = Path(base_dir) / filename
        self.primary_key = "href_path"
        if not Path(base_dir).exists():
            Path(base_dir).mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.entries = {}
        else:
            self.load()

    def load(self):
        with open(self.path, "r") as f:
            self.entries = json.load(f)

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.entries, f, indent=4)

    def safe_key(self, params):
        key = params[self.primary_key]
        key = key.replace("=", "").replace("&", "")
        return key

    def pushOne(self, params):
        if self.safe_key(params) not in self.entries:
            self.entries[self.safe_key(params)] = []
        self.entries[self.safe_key(params)].append(params)
        self.save()

    def pushMany(self, paramss):
        for params in paramss:
            if self.safe_key(params) not in self.entries:
                self.entries[self.safe_key(params)] = []
            self.entries[self.safe_key(params)].append(params)
        self.save()

    def contains(self, params):
        return self.safe_key(params) in self.entries

    def get(self, id):
        if not id:
            return None
        if id not in self.entries:
            return None
        return self.entries[id]

    def unique_href_values(self):
        entries = [row for entry in self.entries.values() for row in entry]
        for entry in entries:
            entry["href_path"] = normalize_qparams(entry["href_path"])
        return filter_unique_hrefs(entries)

    def all_href_values(self):
        return [row for entry in self.entries.values() for row in entry]
