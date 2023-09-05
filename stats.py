import pandas as pd

from ParamsIndexRepo import ParamsIndexRepo, BASE_DIR

visited = ParamsIndexRepo(BASE_DIR, "visited.json")
seen = ParamsIndexRepo(BASE_DIR, "seen.json")

dfv = pd.DataFrame(visited.values())
dfv["image_count"] = dfv["image_urls"].apply(len)

dfv.to_csv("/tmp/artway_index_visited.csv", index=False)

dfs = pd.DataFrame(seen.values())
dfs["id"] = dfs["id"].astype(int)
# dfs['parent'] = dfs['parent'].astype(int)
dfs.sort_values(by="id", inplace=True)
dfs.to_csv("/tmp/artway_index_seen.csv", index=False)
dfs[dfs["id"].duplicated()].to_csv("/tmp/artway_index_seen_dup.csv", index=False)
