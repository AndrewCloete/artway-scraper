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
df = df.drop_duplicates(subset="href_path", keep="last")

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

cols = ["id", "link", "lang", "title", "author", "length", "vm"]
df_show[cols].to_csv(get_master_sheet_path())
print(df_show.shape)
print(df_show["id"].unique().shape)

stats = {
    "list": len_list,
    "show": len_show,
    "show_en": len_show_en,
    "show_nl": len_show_nl,
    "df_unique_id": len_unique_id,
}
print(stats)
