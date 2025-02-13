from math import ceil
import pandas as pd
import csv

from ParamsIndexRepo import (
    ParamsIndexRepo,
    AW_URL,
    BASE_DIR,
    get_bibbook_reference_path,
    get_df_flags,
    get_html_path_named,
    get_wpallimport_cache_path,
    get_df_human,
    get_creator_df,
    get_df_tax,
    get_wpallimport_path,
    get_wpallimport_xlsx,
)

from clean_tags import (
    get_tags_lookup,
    get_types_lookup,
    get_types_to_tags_lookup,
    get_tags_to_lang,
    get_tags_to_category,
)

from dateutil import parser


def get_bibbook_lookup():
    df = pd.read_csv(get_bibbook_reference_path())
    return df.set_index("book")["rename"].to_dict()


LANG = "en"
TAGS_LOOKUP = get_tags_lookup(LANG)
TYPES_LOOKUP = get_types_lookup(LANG)
TYPE_TO_TAGS = get_types_to_tags_lookup(LANG)
LANG_FROM_TAX = get_tags_to_lang(LANG)
CAT_FROM_TAX = get_tags_to_category(LANG)
BOOK_LOOKUP = get_bibbook_lookup()


# Custom parsing function
def fuzzy_date_parser(date_str):
    try:
        # Try to parse the date using dateutil.parser
        return parser.parse(date_str, fuzzy=True).date()
    except (ValueError, TypeError):
        return pd.NaT


def clean_url(url):
    url = url if url.startswith("http") else AW_URL + url
    url = url.replace(" ", "%20")
    return url


def post_content_to_df(posts, html_select) -> pd.DataFrame:
    wpall_posts = []
    for post in posts:
        if "lang" not in post:
            continue
        p = {}
        p["lang"] = post["lang"]
        p["id"] = post["id"]
        p["title"] = post["title"]
        p["Thumbnail title"] = post["title"]
        p["action"] = post["action"] if "action" in post else "none"
        p["image_urls"] = [clean_url(url) for url in post["image_urls"]]

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
    return df.set_index(["id", "lang", "action"])


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

    df["artwork_date"] = (
        df["Artwork Start Date"]
        .apply(fuzzy_date_parser)
        .apply(lambda x: x.year if x == x else None)
    )
    df["artwork_century"] = (
        df["artwork_date"]
        .apply(lambda x: ceil(x / 100) if x == x else None)
        .astype("Int64")
    )
    df["Artwork Century"] = df["Artwork Century"].fillna(df["artwork_century"])

    df["qc_date"] = df["date"].apply(fuzzy_date_parser)
    df["normal_date"] = df["qc_date"].ffill()

    def map_catagory(post_type):
        if post_type in TYPES_LOOKUP:
            new_name = TYPES_LOOKUP[post_type]
            if new_name:
                return new_name
            return post_type
        return "Article"

    df["category"] = df["post_type"].apply(map_catagory)

    df["bib"] = df["Bible References"]

    def clean_bib(index):
        def f(x):
            if x != x:
                return None
            x = x.split(",")[0]
            outer = x.split("-")
            outer = outer + [None] * (2 - len(outer))
            left = outer[0].split(";")
            left = left + [None] * (3 - len(left))
            right = outer[1].split(";") if outer[1] else []
            right = [None] * (2 - len(right)) + right
            if right[1] is not None and right[0] is None:
                right[0] = left[1]

            vars = left + right
            return vars[index]

        return f

    def rename_book(book):
        if book in BOOK_LOOKUP:
            return BOOK_LOOKUP[book]
        return book

    df["bib_book"] = df["bib"].apply(clean_bib(0))
    df["bib_book"] = df["bib_book"].apply(rename_book)
    df["bib_chpS"] = df["bib"].apply(clean_bib(1))
    df["bib_verS"] = df["bib"].apply(clean_bib(2))
    df["bib_chpE"] = df["bib"].apply(clean_bib(3))
    df["bib_verE"] = df["bib"].apply(clean_bib(4))

    return df


def fix_lang_from_tax(row):
    taxs = row["normal_tags"].split(";")
    for tax in taxs:
        if tax in LANG_FROM_TAX:
            return tax
        else:
            return row["real_lang"]


def fix_cat_from_tax(row):
    taxs = row["normal_tags"].split(";")
    for tax in taxs:
        if tax in CAT_FROM_TAX:
            return tax
        else:
            return row["category"]


def fix_tags(row):
    og_tags = [row["Tags"]] if row["Tags"] else []
    clean_tax = [t.strip() for t in row["taxonomies"]]

    tags_set = set(og_tags + clean_tax)
    split_clean = []
    for tax in tags_set:
        if ", " in tax:
            split_clean.extend(tax.split(", "))
        else:
            split_clean.append(tax)

    # Filter tags
    filtered_tax = []
    for tax in split_clean:
        if tax in TAGS_LOOKUP:
            new_tag = TAGS_LOOKUP[tax]
            if new_tag["rename"] == "X":
                pass
            elif not new_tag["rename"]:
                filtered_tax.append(tax)
            else:
                filtered_tax.append(new_tag["rename"])
        else:
            new_tag = "UNKOWN_" + tax
            filtered_tax.append(new_tag)

    filtered_tax = set(filtered_tax)

    post_type = row["post_type"]
    if post_type in TYPE_TO_TAGS:
        new_name = TYPE_TO_TAGS[post_type]
        if new_name:
            filtered_tax.add(new_name)
        else:
            filtered_tax.add(post_type)

    return ";".join(filtered_tax)


COLS = [
    # "count",
    "lang",
    "real_lang",
    "id",
    "action",
    "legacy_ids",
    "normal_date",
    "qc_date",
    "post_type",
    "category",
    "continent",
    "country",
    "period",
    # "taxonomies",
    # "Tags",
    "normal_tags",
    "title",
    "Thumbnail title",
    # "deleted_title",
    # "title_in_content",
    "normal_artist",
    "artist_name_surname",
    "a2z",
    "normal_author",
    # "author",
    # "deleted_author",
    "body_text",
    # "hr",
    "bib_book",
    "bib_chpS",
    "bib_verS",
    "bib_chpE",
    "bib_verE",
    # "Bible References",
    "subtitle",
    "Excerpt",
    "artwork_information",
    "artwork_name",
    "Artwork Start Date",
    "artwork_date",
    "Artwork Century",
    "artwork_century",
    "Artwork End Date",
    "References",
    "image_urls",
]

RENAME_COLS = {
    "real_lang": "Language",
    "id": "Upload ID",
    "normal_date": "Date",
    "period": "Art Period",
    "normal_tags": "Tags",
    "title": "Name",
    "normal_artist": "Artist Name",
    "normal_author": "Author",
    "body_text": "Post Content",
    "bib_book": "Bible Book",
    "Excerpt": "Intro Text",
}

REMOVE_COLS = [
    "count",
    "lang",
    # "date",
    "action",
    "post_type",
    "artist_name_surname",
    "a2z",
    "artwork_date",
    "Artwork Century",
    "artwork_century",
    "References",
    "taxonomies",
    "Tags",
    "deleted_title",
    "title_in_content",
    "author",
    "deleted_author",
    "hr",
    "Bible References",
]

USE_CACHE = False
HTML_SELECT = "clean"

df_tax = get_df_tax().drop(["index"], axis=1)

df_posts = get_post_content_df(html_select=HTML_SELECT, use_cached=USE_CACHE)
df_posts.drop(columns=["title", "index"], inplace=True)


df_human = get_full_df_human()
df_tax = get_df_tax().drop(["index"], axis=1)
df_flags = get_df_flags().drop(["index"], axis=1)

# print(df_human.reset_index()[df_human.reset_index()["id"] == 2412])
# print(df_tax.reset_index()[df_tax.reset_index()["id"] == 2412])
# print(df_flags.reset_index()[df_flags.reset_index()["id"] == 2412])

df = pd.merge(df_human, df_tax, left_index=True, right_index=True)
df = pd.merge(df, df_flags, left_index=True, right_index=True)
df = pd.merge(df, df_posts, left_index=True, right_index=True).reset_index()
# print(df.reset_index()[df.reset_index()["id"] == 2412])


df["title_in_content"] = df.apply(
    lambda row: row["title"] in row["body_text"] if "title" in row else False
)
# df["dup"] = df.duplicated(subset=["lang", "title"], keep=False)
df = df.sort_values(["id"])


# dfg =
#     df.groupby(["lang", "title"])["id"]
#     .apply(lambda x: list(set(x)))
#     .reset_index()
#     .rename(columns={"id": "legacy_ids"})
# )
# print(dfg)


agg_funcs = {
    col: "first"
    for col in df.columns
    if col not in ["lang", "title", "id", "taxonomies"]
}
agg_funcs["id"] = lambda x: list(set(x))
agg_funcs["taxonomies"] = lambda x: [*set().union(*x)]
dfg: pd.DataFrame = df.groupby(["lang", "title"]).agg(agg_funcs).reset_index()

dfg["normal_tags"] = dfg.apply(fix_tags, axis=1)
dfg["real_lang"] = dfg.apply(fix_lang_from_tax, axis=1)
dfg["category"] = dfg.apply(fix_cat_from_tax, axis=1)


dfg["legacy_ids"] = dfg["id"]
dfg["id"] = dfg["legacy_ids"].apply(lambda x: min(x))
dfg["legacy_ids"] = dfg["legacy_ids"].apply(lambda x: ";".join(map(str, x)))
dfg["legacy_ids"] = dfg["legacy_ids"].astype(str)
dfg["count"] = dfg["legacy_ids"].apply(lambda x: len(x))
dfg["taxonomies"] = dfg["taxonomies"].apply(lambda x: ",".join(x) if x else None)

dynamic_cols = [col for col in dfg.columns if col not in COLS]
final_cols = COLS + dynamic_cols
final_cols = [col for col in final_cols if col not in REMOVE_COLS]
dfg = dfg[final_cols].sort_values("id")
# for i in dfg["bib_book"].unique():
#     print(i)

dfg = dfg.rename(columns=RENAME_COLS)
# print(dfg["taxonomies"][~dfg["taxonomies"].isna()])
# print(dfg)
print(dfg[dfg["legacy_ids"].apply(lambda x: "2412" in x)])
print(df.shape)
print(dfg.shape)
# dfg = dfg[dfg["id"] == 56]

if LANG != "en":
    dfg = dfg[dfg["Language"] != "en"]
else:
    dfg = dfg[dfg["Language"] == "en"]

for t in dfg["Tags"]:
    if "UNKOWN_" in t:
        print(t)


# Merge with problems sheet to get items with very larg post content
def merge_problem_items(dfg):
    df_problems = pd.read_csv("data/problem_items.csv")[
        ["Name", "Slug", "Item ID", "Upload ID", "Post Content"]
    ]
    df_problems = df_problems[df_problems["Post Content"].isnull()]
    df_problems = df_problems.drop(columns=["Post Content"])
    dfg = dfg.drop(columns=["Name"])
    dfg = pd.merge(df_problems, dfg, on="Upload ID", how="left").reset_index()
    dfg = dfg[["Name", "Slug", "Item ID", "Upload ID", "Post Content"]]
    return dfg


# dfg = merge_problem_items(dfg)


dfg.to_csv(
    get_wpallimport_path(HTML_SELECT), na_rep="", index=False, quoting=csv.QUOTE_ALL
)
dfg.to_excel(
    get_wpallimport_xlsx(HTML_SELECT),
    na_rep="",
    index=False,
)
#
# df_subset = df  # df[df["id"].isin([1248, 1249, 1250, 1251, 1252, 1253])]
# df_subset.to_csv(get_wpallimport_path(HTML_SELECT), na_rep="", index=False)
