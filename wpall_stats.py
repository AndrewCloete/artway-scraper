from ParamsIndexRepo import (
    get_wpallimport_path,
)
import pandas as pd

df = pd.read_csv(get_wpallimport_path("clean"))
print(df)

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

df["lang"] = df["real_lang"].apply(lambda r: "nl" if r == "nl" else "en")
df_nl = df[df["lang"] == "nl"]
df_en = df[df["lang"] == "en"]


def get_stats(df: pd.DataFrame):
    content = ""
    for col in ["normal_artist", "normal_author", "title"]:
        content += col + "\n"
        content += "TOTAL: " + str(df[col].nunique()) + "\n\n"
    for col in ["real_lang", "post_type", "continent", "country", "period"]:
        content += str(df[col].value_counts()) + "\n"
        content += "TOTAL: " + str(df[col].nunique()) + "\n\n"
    return content


grouped = df.groupby("id")["real_lang"].agg(lambda x: frozenset(x)).reset_index()
combination_counts = grouped["real_lang"].value_counts()
print(combination_counts)

content = "Number of articles per language \n"
content += str(combination_counts) + "\n\n"

content += "*********************** lang == nl **************************\n"
content += get_stats(df_nl)
content += "*********************** lang == en **************************\n"
content += get_stats(df_en)
content += "*********************** lang == all **************************\n"
content += get_stats(df)


print(content)

with open("/tmp/artway_stats.txt", "w") as file:
    file.write(content)
