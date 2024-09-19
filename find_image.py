import ast
from ParamsIndexRepo import (
    get_wpallimport_path,
)
import pandas as pd

df: pd.DataFrame = pd.read_csv(get_wpallimport_path("clean"))


# img_cols = [c for c in df.columns if "image" in c]
# num_cols = [c.split("_")[1] for c in img_cols]
# for col in img_cols:
#     (_, num) = col.split("_")
#     df[num] = df[col].str.contains(r"\s", na=False)


def blanks(urls_str):
    urls = ast.literal_eval(urls_str)
    out = ""
    i = 0
    for url in urls:
        if " " in url.strip():
            out += str(i) + "|"
        i += 1
    return out


def blank_urls(urls_str):
    urls = ast.literal_eval(urls_str)
    return [url for url in urls if " " in url.strip()]


def fix_urls(urls_str):
    urls = ast.literal_eval(urls_str)
    return [url.replace(" ", "-") for url in urls if " " in url.strip()]


df["blanks"] = df["image_urls"].apply(blanks)
df["culprits"] = df["image_urls"].apply(blank_urls)
df["fixed"] = df["image_urls"].apply(fix_urls)
df[["id", "real_lang", "title", "blanks", "culprits", "fixed"]].to_csv(
    "/tmp/image_urls_with_space.csv", index=False
)
