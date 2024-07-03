import pandas as pd

from ParamsIndexRepo import (
    ParamsIndexRepo,
    AW_URL,
    BASE_DIR,
    get_html_path_named,
    get_wpallimport_cache_path,
    get_wpallimport_path,
    get_df_human,
)


def post_content_to_df(posts, html_select) -> pd.DataFrame:
    wpall_posts = []
    for post in posts:
        if "lang" not in post:
            continue
        p = {}
        p["lang"] = post["lang"]
        p["id"] = post["id"]
        p["title"] = post["title"]
        p["image_urls"] = [
            url if url.startswith("http") else AW_URL + url
            for url in post["image_urls"]
        ]

        html_path = get_html_path_named(
            post["id"], post["lang"], post["title"], html_select
        )

        with open(html_path, "r") as f:
            content = f.read()
            p["body_text"] = content

        for idx, url in enumerate(p["image_urls"]):
            p[f"image_{idx}"] = url

        wpall_posts.append(p)
    return pd.DataFrame(wpall_posts)


def get_post_content_df(html_select: str, use_cached: bool) -> pd.DataFrame:
    posts_df_path = get_wpallimport_cache_path(html_select)

    def get() -> pd.DataFrame:
        if use_cached:
            return pd.read_csv(posts_df_path)
        else:
            visited = ParamsIndexRepo(BASE_DIR, "visited.json")
            posts = visited.unique_href_values()
            df_posts = post_content_to_df(posts, html_select)
            df_posts.to_csv(posts_df_path, na_rep="", index=False)
            return df_posts

    df = get()
    df = df.astype({"id": "int64"})
    return df.set_index(["id", "lang"])


USE_CACHE = False
HTML_SELECT = "clean"
df_posts = get_post_content_df(html_select=HTML_SELECT, use_cached=USE_CACHE)
df_posts.drop(columns=["title"], inplace=True)
df_human = get_df_human()
df = pd.merge(df_human, df_posts, left_index=True, right_index=True).reset_index()
df_subset = df[df["id"].isin([1248, 1249, 1250, 1251, 1252, 1253])]
df_subset.to_csv(get_wpallimport_path(HTML_SELECT), na_rep="")
