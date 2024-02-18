import pandas as pd
from common import *

from ParamsIndexRepo import ParamsIndexRepo, BASE_DIR

visited = ParamsIndexRepo(BASE_DIR, "visited.json")
seen = ParamsIndexRepo(BASE_DIR, "seen.json")

dfv = pd.DataFrame(visited.values())
dfv["image_count"] = dfv["image_urls"].apply(len)

dfv.to_csv("/tmp/artway_index_visited.csv", index=False)

dfs = pd.DataFrame(seen.values())
dfs["id"] = dfs["id"].astype(int)
dfs["p_id"] = dfs["p_id"].astype(int)
dfs.sort_values(by="id", inplace=True)
dfs.to_csv("/tmp/artway_index_seen.csv", index=False)


# I'm making the assumption that parents existed before children. So to solve
# the problem of parent links nested inside children pages, I'm applying the
# filter to only keep records where the p_id < id
# "pl" for "parent limit"
cols = [col for col in dfs.columns if col.startswith("p_p_")]
cols.extend(["location", "p_location"])
print(cols)

dfs_pl = dfs[dfs["p_id"] <= dfs["id"]]
dfs_pl.drop(columns=cols, axis=1, inplace=True)
dfs_pl.drop_duplicates(keep="first", inplace=True)  # Drop exact duplicates


filter_self_parent = (
    filter_char(dfs_pl)
    | filter_continent(dfs_pl)
    | filter_period(dfs_pl)
    | filter_country(dfs_pl)
)
print(dfs_pl[filter_self_parent])

# The above limit is required, but not sufficien. Additionally, we can manually
# specify ids that should not be in a parent-child relationship and remove them
# HOWEVER, exact p_id == id must be allowed for "country", "contintent" etc
MUTUALLY_EXCLUSIVE_IDS = [7, 8, 9]
filter_mutually_exclusive = ~(
    dfs_pl["p_id"].isin(MUTUALLY_EXCLUSIVE_IDS)
    & dfs_pl["id"].isin(MUTUALLY_EXCLUSIVE_IDS)
)

dfs_pl = dfs_pl[filter_mutually_exclusive | filter_self_parent]
dfs_pl.fillna("", inplace=True)
dfs_pl.to_csv("/tmp/artway_index_seen_limit.csv", index=False, na_rep="")


df_id = dfs[~dfs["id"].duplicated(keep="first")]
df_id = df_id[["id", "title"]].set_index("id")


# dfs_parents = dfs.groupby(["id", "title"])["p_id"].apply(",".join)
# print(dfs_parents)
# dfs_parents.to_csv("/tmp/artway_parents.csv")
