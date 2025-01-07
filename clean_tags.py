import pandas as pd

from ParamsIndexRepo import get_tags_path, get_taxonomies_path

df_tax = pd.read_csv(get_taxonomies_path())
# ==== Get a unique list of tags
df_tags = df_tax[["lang", "tags"]]

df_tags["tags"] = df_tags["tags"].replace("", None)
# Split the tags and explode into individual rows
df_exploded = df_tags.assign(tag=df_tags["tags"].str.split(",")).explode("tag")
df_exploded["tag"] = df_exploded["tag"].str.strip()
# Drop duplicates and reset the index
df_cleaned = df_exploded[["lang", "tag"]].drop_duplicates().reset_index(drop=True)
# Drop any rows where 'tag' is NaN
df_cleaned = df_cleaned.dropna(subset=["tag"])
df_cleaned.to_csv(get_tags_path(), index=False)
