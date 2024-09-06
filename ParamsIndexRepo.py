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


def get_master_sheet_path():
    return Path(BASE_DIR) / "master_sheet.csv"


def get_human_sheet_path():
    return Path(BASE_DIR) / "human_sheet.csv"


def get_authors_path(kind: str | None):
    match kind:
        case None:
            return Path(BASE_DIR) / "authors.csv"
        case "human":
            return Path(BASE_DIR) / "human_authors.csv"
        case "normal":
            return Path(BASE_DIR) / "normal_authors.csv"


def get_creator_path(prefix: str, kind: str):
    return Path(BASE_DIR) / f"{prefix}_{kind}.csv"


def get_artists_path():
    return Path(BASE_DIR) / "artists.csv"


def get_similars_path():
    return Path(BASE_DIR) / "similars.csv"


def get_filtered_similars_path():
    return Path(BASE_DIR) / "similars_filtered.csv"


def get_df_human():
    df_human = pd.read_csv(get_human_sheet_path())
    df_human = df_human.astype({"id": "int64"})
    return df_human.set_index(["id", "lang"])


def get_wpallimport_cache_path(html_select):
    return Path(BASE_DIR) / f"wpall_import_{html_select}_cache.csv"


def get_wpallimport_path(html_select):
    return Path(BASE_DIR) / f"wpall_import_{html_select}.csv"


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
