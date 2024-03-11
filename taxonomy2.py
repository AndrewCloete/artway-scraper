import pandas as pd
import common


df = pd.read_csv("/tmp/artway_index_seen_limit.csv")
df["pk"] = df["id"].astype(str) + "_" + df["lang"]
df["id"] = df["id"].astype(int)
df["p_id"] = df["p_id"].astype(int)
df.fillna("", inplace=True)

lookup_dfs = {
    "country": df[common.filter_country(df)][["title", "lang", "country"]],
    "period": df[common.filter_period(df)][["title", "lang", "period"]],
    "continent": df[common.filter_continent(df)][["title", "lang", "continent"]],
}

CATEGORIES = lookup_dfs.keys()

lookup = {
    cat: {
        f"{int(r[cat])}_{r['lang']}": r["title"]
        for r in lookup_dfs[cat].to_dict(orient="records")
    }
    for cat in CATEGORIES
}


def replace_category_ids(cat):
    def func(r):
        key = f"p_{cat}"
        if key not in r:
            return ""
        id = r[key]
        if id == "" or pd.isna(id):
            return ""
        lookup_key = f"{int(id)}_{r['lang']}"
        return lookup[cat][lookup_key]

    return func


for cat in CATEGORIES:
    df[f"p_{cat}"] = df.apply(replace_category_ids(cat), axis=1)

title_lookups = {f"{r['pk']}": r["title"] for r in df.to_dict(orient="records")}

p_ids_lookups = {}
for r in df.to_dict(orient="records"):
    if r["pk"] not in p_ids_lookups:
        p_ids_lookups[r["pk"]] = []
    if r["p_id"]:
        p_ids_lookups[r["pk"]].append(r["p_id"])

TAX = ["p_char", "p_country", "p_period", "p_continent", "author", "vm"]


def extract_taxonomies(r):
    def has(key):
        return key in r and r[key] != "" and ~pd.isna(r[key])

    t = {}
    tags = []
    for tax in TAX:
        if has(tax):
            t[tax] = r[tax]

    tags = set()

    def add_tag(tag):
        if not tag:
            return
        tags.add(tag)

    # if has("vm"):
    #     add_tag("vm")

    for p_id in p_ids_lookups[r["pk"]]:
        p_id_lookup = f"{p_id}_{r['lang']}"
        if p_id_lookup in title_lookups:
            p_title = title_lookups[p_id_lookup]
            add_tag(p_title)

    t["tags"] = ",".join(tags)

    return t


items = []

for i, dfg in df.groupby(["id", "lang"]):
    taxonomies = {"id": i[0], "lang": i[1]}
    for r in dfg.to_dict(orient="records"):
        taxonomies = {
            "title": r["title"],
            "lang": r["lang"],
            "type": r["type"],
            "action": r["action"],
            **taxonomies,
            **extract_taxonomies(r),
        }
    items.append(taxonomies)


df_tax = pd.DataFrame(items)
df_tax.to_csv("/tmp/taxonomies.csv")

# print("-------------------------------------")
# print(df_country)
# print("-------------------------------------")
# print(df_period)
# print("-------------------------------------")
# print(df_continent)
# print("-------------------------------------")
