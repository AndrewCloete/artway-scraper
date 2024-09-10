from ParamsIndexRepo import (
    get_creator_df,
    get_creator_path,
)


def normalize_creator(kind: str):
    df_human_creator = get_creator_df("human", kind)
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


normalize_creator("artists")
