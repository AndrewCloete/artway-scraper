from pathlib import Path
import json

BASE_DIR = "/tmp/artway"


def get_params_dir(params):
    return (
        Path(BASE_DIR)
        / "content"
        / f"{params['id']}_{params['action']}_{params['title']}"
    )


class ParamsIndexRepo:
    def __init__(self, base_dir, filename):
        self.base_dir = base_dir
        self.filename = filename
        self.path = Path(base_dir) / filename
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

    def pushOne(self, params):
        self.entries[params["id"]] = params
        self.save()

    def pushMany(self, paramss):
        for params in paramss:
            self.entries[params["id"]] = params
        self.save()

    def contains(self, params):
        return params["id"] in self.entries

    def get(self, id):
        if not id:
            return None
        if not id in self.entries:
            return None
        return self.entries[id]

    def values(self):
        return self.entries.values()
