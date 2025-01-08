import pandas as pd

from ParamsIndexRepo import (
    get_tags_reference_path,
    get_tags_path,
    get_taxonomies_path,
    get_post_type_changes_path,
)


def original_list_of_tags_for_otto():
    df_tax = pd.read_csv(get_taxonomies_path())
    # ==== Get a unique list of tags
    df_tags = df_tax[["lang", "tags"]]

    df_tags["tags"] = df_tags["tags"].replace("", None)
    # Split the tags and explode into individual rows
    df_exploded = df_tags.assign(tag=df_tags["tags"].str.split(",")).explode("tag")
    df_exploded["tag"] = df_exploded["tag"].str.strip()
    # Drop duplicates and reset the index
    df_cleaned = df_exploded[["lang", "tag"]].drop_duplicates().reset_index(drop=True)
    # Drop any rows where 'tag' is NaN
    df_cleaned = df_cleaned.dropna(subset=["tag"])
    df_cleaned.to_csv(get_tags_path(), index=False)


def get_post_type_changes():
    df = pd.read_csv(get_post_type_changes_path())
    df_tags = df[df["to_tags"]]
    df_types = df[~df["to_tags"]]
    return (df_tags, df_types)


def get_tags_reference(lang: str):
    df = pd.read_csv(get_tags_reference_path())
    return df[df["lang"] == lang]


def get_tags_lookup(lang: str):
    df = get_tags_reference(lang)
    df["rename"] = df["rename"].fillna(False)
    records = df.to_dict("records")
    return {r["tag"]: r for r in records}


def get_list_of_valid_tags(lang: str):
    df = get_tags_reference(lang)
    df = df[df["rename"] != "X"]
    df_tags, _ = get_post_type_changes()

    return pd.DataFrame(
        list(
            list(set(df["rename"].fillna(df["tag"]).tolist()))
            + list(df_tags["new_name"].fillna(df_tags["category"])),
        )
    )


def get_list_of_valid_types():
    _, df_types = get_post_type_changes()
    return pd.DataFrame(
        list(df_types["new_name"].fillna(df_types["category"])),
    )


def get_types_lookup():
    _, df_types = get_post_type_changes()
    df_types["new_name"] = df_types["new_name"].fillna(False)
    df_types = df_types.set_index("category")["new_name"]
    return df_types.to_dict()


def get_types_to_tags_lookup():
    df_tags, _ = get_post_type_changes()
    df_tags["new_name"] = df_tags["new_name"].fillna(False)
    df_tags = df_tags.set_index("category")["new_name"]
    return df_tags.to_dict()


if __name__ == "__main__":
    print(get_list_of_valid_tags("en"))  # .to_csv("data/list_of_tags.csv")
    get_list_of_valid_types().to_csv("data/list_of_posts.csv")
    # print(get_list_of_valid_tags("nl"))

    print(get_tags_lookup("en"))
    print()
    print(get_types_lookup())
    print()
    print(get_types_to_tags_lookup())
