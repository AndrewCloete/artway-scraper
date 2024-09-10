from math import ceil
import pandas as pd

from ParamsIndexRepo import (
    ParamsIndexRepo,
    AW_URL,
    BASE_DIR,
    get_html_path_named,
    get_wpallimport_cache_path,
    get_df_human,
    get_creator_df,
    get_df_tax,
)

from dateutil import parser


# Custom parsing function
def fuzzy_date_parser(date_str):
    try:
        # Try to parse the date using dateutil.parser
        return parser.parse(date_str, fuzzy=True).date()
    except (ValueError, TypeError):
        return pd.NaT


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
    df["index"] = df["id"] + "_" + df["lang"]
    df = df.astype({"id": "int64"})
    return df.set_index(["id", "lang"])


def get_full_df_human():
    df = get_df_human()
    df.drop(
        [
            "link",
            "done",
            "artist_name",
            "artist_surname",
            "artist_bio",
            "author_bio",
            "comments",
            "length",
            "table_len",
            "max_table_image_count",
        ],
        axis=1,
        inplace=True,
    )

    def explode(df, key):
        df = df.explode("articles")
        df["index"] = df.apply(lambda r: str(r["articles"]) + "_" + r["lang"], axis=1)
        return df.set_index("index")[key].to_dict()

    lookup_authors = explode(get_creator_df("normal", "authors"), "name_surname")
    lookup_artists = explode(get_creator_df("normal", "artists"), "name_surname")
    lookup_a2z = explode(get_creator_df("normal", "artists"), "surname")

    df["normal_author"] = df["index"].apply(
        lambda i: lookup_authors[i] if i in lookup_authors else None
    )
    df["normal_artist"] = df["index"].apply(
        lambda i: lookup_artists[i] if i in lookup_artists else None
    )
    df["a2z"] = df["index"].apply(
        lambda i: lookup_a2z[i][0].upper() if i in lookup_a2z else None
    )

    df["artwork_date"] = df["Artwork Start Date"].apply(fuzzy_date_parser)
    df["artwork_century"] = (
        df["artwork_date"]
        .apply(lambda x: ceil(x.year / 100 + 1) if x == x else None)
        .astype("Int64")
    )

    df["normal_date"] = df["date"].apply(fuzzy_date_parser).ffill()
    return df


USE_CACHE = False
HTML_SELECT = "clean"
df_human = get_full_df_human()
df_posts = get_post_content_df(html_select=HTML_SELECT, use_cached=USE_CACHE)
df_posts.drop(columns=["title", "image_urls"], inplace=True)

df_human = get_full_df_human()
df_tax = get_df_tax()
df = pd.merge(df_human, df_tax, left_index=True, right_index=True)
df = pd.merge(df, df_posts, left_index=True, right_index=True).reset_index()
df["dup"] = df.duplicated(subset=["lang", "title"], keep=False)
df = df.sort_values(["id"])

# dfg =
#     df.groupby(["lang", "title"])["id"]
#     .apply(lambda x: list(set(x)))
#     .reset_index()
#     .rename(columns={"id": "legacy_ids"})
# )
# print(dfg)


agg_funcs = {col: "first" for col in df.columns if col not in ["lang", "title", "id"]}
agg_funcs["id"] = lambda x: list(set(x))
dfg = df.groupby(["lang", "title"]).agg(agg_funcs).reset_index()
dfg["legacy_ids"] = dfg["id"]
dfg["id"] = dfg["legacy_ids"].apply(lambda x: min(x))
dfg["count"] = dfg["legacy_ids"].apply(lambda x: len(x))
print(dfg)
print(df.shape)
print(dfg.shape)
#
# df_subset = df  # df[df["id"].isin([1248, 1249, 1250, 1251, 1252, 1253])]
# df_subset.to_csv(get_wpallimport_path(HTML_SELECT), na_rep="", index=False)
