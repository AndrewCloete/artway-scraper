from operator import itemgetter
from ParamsIndexRepo import ParamsIndexRepo, BASE_DIR, get_html_path_named
import shutil


visited = ParamsIndexRepo(BASE_DIR, "visited.json")

posts = visited.unique_href_values()


def copy_clean(post):
    id, title = itemgetter("id", "title")(post)
    lang = post["lang"] if "lang" in post else "none"

    def filename(t):
        return f"{id}_{lang}_{title}_{t}.html".replace("/", "")

    path_original = get_html_path_named(id, lang, title, "original")
    new_original = "/tmp/content_flat/" + filename("original")
    shutil.copy(path_original, new_original)

    path_clean = get_html_path_named(id, lang, title, "clean")
    new_clean = "/tmp/content_flat/" + filename("clean")
    shutil.copy(path_clean, new_clean)


for post in posts:
    flag = copy_clean(post)
