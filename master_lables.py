from ParamsIndexRepo import (
    ParamsIndexRepo,
    BASE_DIR,
    AW_URL,
    get_master_sheet_path,
)

import pandas as pd


visited = ParamsIndexRepo(BASE_DIR, "visited.json")

posts = visited.unique_href_values()

df = pd.DataFrame(posts)

df_list = df[df["action"] == "list"]
df_show = df[df["action"] == "show"]
df_show["link"] = df_show["href_path"].apply(lambda x: f"{AW_URL}/content.php?{x}")

df_show_en = df_show[df_show["lang"] == "en"]
df_show_nl = df_show[df_show["lang"] == "nl"]
df_unique_id = df["id"].unique()


len_list = df_list.shape[0]
len_show = df_show.shape[0]
len_show_en = df_show_en.shape[0]
len_show_nl = df_show_nl.shape[0]
len_unique_id = df_unique_id.shape[0]

df_show["vm"] = df_show["vm"].notna()


def remove_author_from_title(row):
    row["title"] = row["title"].replace(str(row["author"]), "").replace("-", "").strip()
    row["author"] = (
        row["author"].replace("door ", "").strip()
        if isinstance(row["author"], str)
        else None
    )
    row["post_type"] = "vm" if row["vm"] else None

    if ", " in row["title"]:
        artist = row["title"].split(", ")
        if len(artist) == 1:
            row["artist_name"] = artist[0]
        if len(artist) == 2:
            row["artist_surname"] = artist[0]
            row["artist_name"] = artist[1]
    return row


df_show = df_show.apply(remove_author_from_title, axis=1)
cols = [
    "id",
    "link",
    "lang",
    "title",
    "author",
    "length",
    "post_type",
    "artist_name",
    "artist_surname",
]
df_show[cols].to_csv(get_master_sheet_path(), index=False)

stats = {
    "list": len_list,
    "show": len_show,
    "show_en": len_show_en,
    "show_nl": len_show_nl,
    "df_unique_id": len_unique_id,
}
print(stats)
print(len(df_show["id"]) - len(df_show["id"].drop_duplicates()))
print(len(df_show[df_show["vm"] == True]["author"].unique()))
