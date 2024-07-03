from ParamsIndexRepo import (
    ParamsIndexRepo,
    BASE_DIR,
    get_authors_path,
    get_human_sheet_path,
)
import pandas as pd


visited = ParamsIndexRepo(BASE_DIR, "visited.json")

posts = visited.unique_href_values()

df_human = pd.read_csv(get_human_sheet_path())
df_human = df_human.astype({"id": "int64"})
df_human.set_index(["id", "lang"], inplace=True)

print(df_human.groupby("post_type").count()[["done"]])

df_artists = df_human[
    ["artist_name_surname", "artist_name", "artist_surname", "artist_bio"]
]

print()
notna_counts = df_human.count()
print(notna_counts[["artist_name", "artist_bio"]])


def get_authors(df_human: pd.DataFrame) -> pd.DataFrame:
    def remove_non_printable(s):
        if not isinstance(s, str):
            return s
        return s.strip()

    df = df_human.reset_index()[["id", "lang", "author", "author_bio"]].copy()
    df["author"] = df["author"].apply(remove_non_printable)
    df["author_bio"] = df["author_bio"].apply(remove_non_printable)

    # Collect the list of articles each author has written
    df_article_list = (
        df.reset_index()
        .groupby(["lang", "author"])["id"]
        .apply(lambda x: list(set(x)))
        .reset_index()
        .rename(columns={"id": "articles"})
    )

    df = df[["lang", "author", "author_bio"]]

    # Create "has_bio" df
    df_has_bio = df[~df["author_bio"].isna()][["lang", "author"]].drop_duplicates()
    df_has_bio["has_bio"] = True

    # Drop duplicates but keep NA
    df_unique = df.drop_duplicates()
    df_na = df[df["author"].isna() | df["author_bio"].isna()]
    df_unique_with_na = (
        pd.concat([df_na, df_unique]).sort_values("author").drop_duplicates()
    )

    df_unique_with_na_and_has_bio = pd.merge(
        df_unique_with_na, df_has_bio, on=["lang", "author"], how="outer"
    )

    # Filter for items without bio, but has_bio
    filter = (
        df_unique_with_na_and_has_bio["author_bio"].isna()
        & df_unique_with_na_and_has_bio["has_bio"]
    )
    df_unique_with_na_and_has_bio = df_unique_with_na_and_has_bio[~filter]

    return pd.merge(
        df_unique_with_na_and_has_bio,
        df_article_list,
        on=["lang", "author"],
        how="outer",
    )


df_authors = get_authors(df_human)
print(df_authors)
df_authors.to_csv(get_authors_path(), na_rep="")
