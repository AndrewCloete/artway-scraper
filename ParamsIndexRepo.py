from pathlib import Path
import json

BASE_DIR = "/Users/user/Workspace/artway-scraper/data"
AW_URL = "https://www.artway.eu"


def get_params_dir(id, title):
    return Path(BASE_DIR) / "content" / f"{id}_{title}"


def get_html_path(id, title):
    return get_params_dir(id, title) / "original.html"


def get_flags_path():
    return Path(BASE_DIR) / "flags.csv"


def get_html_path_named(id, title, name):
    return get_params_dir(id, title) / f"{name}.html"


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

    def values(self):
        return [row for entry in self.entries.values() for row in entry]
