import json
from textwrap import indent
import pandas as pd

db = {}

ID_TAGS = ["continent", "country", "period"]


def build_tag_lookup(records):
    tag_lookup = {}
    for r in records:
        for tag_name in ID_TAGS:
            if r[tag_name] and not pd.isna(r[tag_name]):
                if tag_name not in tag_lookup:
                    tag_lookup[tag_name] = {}
                tag_lookup[tag_name][r["id"]] = r["title"]
    return tag_lookup


def extract_tags(record, tag_lookup):
    def extract_id_tags(record):
        id_tags = {}
        for tag in [f"p_{tag}" for tag in ID_TAGS]:
            if tag in r and r[tag] and not pd.isna(r[tag]):
                id_tags[tag] = r[tag_name]
        for k, v in record.items():
            if not v:
                continue
            if not k.startswith("p_"):
                continue
            if k.startswith("p_p_"):
                continue
            if k in ["p_location", "p_action", "p_menuid"]:
                continue
            id_tags[k.split("p_")[1]] = v
        return id_tags

    def has_value(r, key):
        return key in r and r[key] and not pd.isna(r[key])

    tags = {}
    missing_tags = set()
    if (has_value(record, "p_char"))
        tags["p_char"] = record["p_char"]

    for id_tag in [f"p_{tag}" for tag in ID_TAGS]:
        if (has_value(record,id_tag))
            if tag_name not in tag_lookup:
                missing_tags.add(tag_name)
                continue

            tag_value = tag_lookup[tag_name][tag_p_id]
            tags[tag_name] = tag_value
                tags[id_tag] = record[id_tag]



    for tag_name, tag_p_id in extract_id_tags(record).items():
        if pd.isna(tag_p_id):
            continue
        if tag_name == "char":
            tags[tag_name] = tag_p_id
            continue

        if tag_name == "id":
            if tag_p_id not in db:
                continue
            tags[db[tag_p_id]["title"]] = True
            continue

        if tag_name not in tag_lookup:
            missing_tags.add(tag_name)
            continue
        if tag_p_id not in tag_lookup[tag_name]:
            missing_tags.add(tag_p_id)
            continue

        tag_value = tag_lookup[tag_name][tag_p_id]
        tags[tag_name] = tag_value
    return (tags, missing_tags)


df = pd.read_csv("/tmp/artway_index_seen_limit.csv")
df["id"] = df["id"].astype(int)
df["p_id"] = df["p_id"].astype(int)
records = df.to_dict(orient="records")

tag_lookup = build_tag_lookup(records)

# First pass, just add all the titles to the database
for r in records:
    db[r["id"]] = {"id": r["id"], "title": r["title"]}
    if "vm" in r and not pd.isna(r["vm"]):
        db[r["id"]] = {**db[r["id"]], "vm": True}
    if "lang" in r:
        db[r["id"]] = {**db[r["id"]], r["lang"]: True}


print(len(records))
# Second pass, keep adding tags to each article
for r in records:
    # if r["action"] == "list":
    #     continue
    (ID_TAGS, missing) = extract_tags(r, tag_lookup)
    db[r["id"]] = {**db[r["id"]], **ID_TAGS}

# print(db)
# df_tax = pd.DataFrame(db.values())
with open("/tmp/artway_tax.json", "w") as f:
    json.dump([*db.values()], f, indent=2)

# print(df_tax)
# df_tax.to_csv("/tmp/taxonomies.csv")
