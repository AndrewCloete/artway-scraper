import pandas as pd

db = {}
tag_dict = {}

def extract_id_tags(r):
    id_tags = {}
    for k,v in r.items():
        if not v:
            continue
        if not k.startswith("p_"):
            continue
        if k.startswith("p_p_"):
            continue
        if k in ["p_location", "p_action", "p_menuid"]:
            continue;
        id_tags[k.split("p_")[1]] = v
    return id_tags

missing_tags = set()
def extract_tags(r):
    tags = {}
    for tag_name,tag_p_id in extract_id_tags(r).items():
        if pd.isna(tag_p_id):
            continue
        if tag_name == "char":
            tags[tag_name] = tag_p_id 
            continue

        if tag_name == "id":
            if tag_p_id not in db:
                continue
            tags[db[tag_p_id]['title']] = True
            continue

        if tag_name not in tag_dict:
            missing_tags.add(tag_name)
            continue
        if tag_p_id not in tag_dict[tag_name]:
            missing_tags.add(tag_p_id)
            continue

        tag_value = tag_dict[tag_name][tag_p_id]
        tags[tag_name] = tag_value
    return tags

df = pd.read_csv("/tmp/artway_index_seen.csv")
df["id"] = df["id"].astype(int)
records = df.to_dict(orient='records')

tags = ["continent", "country", "period"]
for r in records:
    for tag_name in tags:
        if r[tag_name] and not pd.isna(r[tag_name]):
            if tag_name not in tag_dict:
                tag_dict[tag_name]= {}
            tag_dict[tag_name][r['id']]= r['title']

# First pass, just add all the titles to the database
for r in records:
    db[r['id']] = {"id": r["id"], "title": r['title']}
    if "vm" in r and not pd.isna(r["vm"]):
        db[r['id']] = {**db[r['id']], "vm": True} 
    if "lang" in r:
        db[r['id']] = {**db[r['id']], r["lang"]: True} 


# Second pass, keep adding tags to each article
for r in records:
    if r['action'] == "list":
        continue
    db[r['id']] = {**db[r['id']], **extract_tags(r)} 

# print(db)
df_tax = pd.DataFrame(db.values())
print(df_tax)
df_tax.to_csv("/tmp/taxonomies.csv")


