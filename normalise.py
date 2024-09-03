import ast
from ParamsIndexRepo import (
    get_df_human,
    get_creator_path,
    get_artists_path,
)

import pandas as pd


def normalize_creator(kind: str):
    def parse_articles(article_str: str):
        if "[" not in article_str:
            return []
        articles = ast.literal_eval(article_str)
        return [int(x) for x in articles]

    df_human_creator = pd.read_csv(
        str(get_creator_path("human", kind)),
        index_col=0,
        converters={"articles": parse_articles},
    )
    print(df_human_creator.shape)

    df_human_creator["name_surname"] = df_human_creator["name_surname"].str.split(
        r" and | en "
    )
    df_human_creator["count"] = df_human_creator["name_surname"].apply(
        lambda x: len(x) if x == x else 0
    )
    df_human_creator = df_human_creator.explode("name_surname")
    df_human_creator["bio"] = df_human_creator["bio"].fillna("")

    groups = ["lang", "count", "name_surname"]
    if kind == "artists":
        groups += ["name", "surname"]
    groups += ["bio"]
    df_normal_creator = df_human_creator.groupby(groups, as_index=False).agg(
        {"articles": "sum"}
    )

    df_normal_creator["articles"] = df_normal_creator["articles"].apply(
        lambda x: sorted(list(set(x)))
    )
    df_normal_creator = df_normal_creator.sort_values(by=["name_surname"])
    print(df_normal_creator.shape)

    df_normal_creator.to_csv(get_creator_path("normal", kind))


def artists():
    df_human = get_df_human()
    df_human["artist_bio"] = df_human["artist_bio"].fillna("")
    df_artists = (
        df_human.reset_index()
        .groupby(
            [
                "lang",
                "artist_name_surname",
                "artist_name",
                "artist_surname",
                "artist_bio",
            ]
        )["id"]
        .apply(lambda x: list(set(x)))
        .reset_index()
        .rename(columns={"id": "articles"})
    ).sort_values(by=["artist_name_surname"])

    print(df_artists.shape)
    df_artists.to_csv(get_artists_path())


normalize_creator("artists")
