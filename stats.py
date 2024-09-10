import pandas as pd
import common

from ParamsIndexRepo import ParamsIndexRepo, BASE_DIR, get_seen_limit_path

seen = ParamsIndexRepo(BASE_DIR, "seen.json")

df = pd.DataFrame(seen.all_href_values())
df["id"] = df["id"].astype(int)
df["p_id"] = df["p_id"].astype(int)
df.sort_values(by="id", inplace=True)


# I'm making the assumption that parents existed before children. So to solve
# the problem of parent links nested inside children pages, I'm applying the
# filter to only keep records where the p_id < id
# "pl" for "parent limit"
p_cols = [col for col in df.columns if col.startswith("p_p_")]
p_cols.extend(["location", "p_location"])

df_pl = df[df["p_id"] <= df["id"]]
df_pl.drop(columns=p_cols, axis=1, inplace=True)
df_pl.drop_duplicates(keep="first", inplace=True)  # Drop exact duplicates


filter_self_parent = (
    common.filter_char(df_pl)
    | common.filter_continent(df_pl)
    | common.filter_period(df_pl)
    | common.filter_country(df_pl)
)

# The above limit is required, but not sufficien. Additionally, we can manually
# specify ids that should not be in a parent-child relationship and remove them
# HOWEVER, exact p_id == id must be allowed for "country", "contintent" etc
MUTUALLY_EXCLUSIVE_IDS = [7, 8, 9]
filter_mutually_exclusive = ~(
    df_pl["p_id"].isin(MUTUALLY_EXCLUSIVE_IDS)
    & df_pl["id"].isin(MUTUALLY_EXCLUSIVE_IDS)
)

df_pl = df_pl[filter_mutually_exclusive | filter_self_parent]
df_pl.fillna("", inplace=True)
df_pl.to_csv(get_seen_limit_path(), index=False, na_rep="")


# df_id = df[~df["id"].duplicated(keep="first")]
# df_id = df_id[["id", "title"]].set_index("id")


# df_parents = df.groupby(["id", "title"])["p_id"].apply(",".join)
# print(df_parents)
# df_parents.to_csv("/tmp/artway_parents.csv")
