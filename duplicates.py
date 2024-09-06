import ast
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from joblib import Parallel, delayed
from operator import itemgetter
from ParamsIndexRepo import (
    ParamsIndexRepo,
    BASE_DIR,
    get_similars_path,
    get_filtered_similars_path,
    get_html_path_named,
    get_df_human,
)

import pandas as pd
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class Similar:
    id: str
    title: str
    score: float


@dataclass
class Record:
    id: str
    title: str
    content: str
    similar: List[Similar]


def get_similar_df(threshold) -> pd.DataFrame:
    if get_similars_path().exists():
        print("Using cached similars")
        df = pd.read_csv(get_similars_path())
        df["similar"] = df["similar"].apply(ast.literal_eval)
        return df

    print("No cached similars. Calculating...")

    visited = ParamsIndexRepo(BASE_DIR, "visited.json")
    posts = visited.unique_href_values()

    def get_post(post) -> Optional[Record]:
        id, title = itemgetter("id", "title")(post)
        lang = post["lang"] if "lang" in post else "none"
        action = post["action"] if "action" in post else None
        if action == "list":
            return None
        lang = post["lang"] if "lang" in post else "none"
        path_original = get_html_path_named(id, lang, title, "clean")
        with open(path_original, "r") as f:
            content = f.read()

        return Record(f"{id}{lang}", title, content, [])

    records: List[Record] = [p for p in [get_post(p) for p in posts] if p]

    # Vectorize the posts
    vectorizer = TfidfVectorizer(stop_words="english")
    print("Vectorizing")
    tfidf_matrix = vectorizer.fit_transform([r.content for r in records])

    # Function to calculate similarity for a given pair of indices
    def compute_similarity(i, j):
        return cosine_similarity(tfidf_matrix[i], tfidf_matrix[j])[0][0]

    # Use parallel processing to compute all pairwise similarities
    print("Comparing")
    similarities = Parallel(n_jobs=-1)(
        delayed(compute_similarity)(i, j)
        for i in range(len(records))
        for j in range(i + 1, len(records))
    )

    idx = 0
    for i in range(len(records)):
        r = records[i]
        for j in range(i + 1, len(records)):
            s = records[j]
            score = similarities[idx]
            if score >= threshold:
                r.similar.append(Similar(id=s.id, title=s.title, score=score))
            idx += 1

    similars = set()
    dicts = []
    for r in records:
        # Skip over articles we've already listed as a similar somwhere else
        if r.id in similars:
            continue
        if len(r.similar) == 0:
            continue
        # Add to similars to skip over later
        for s in r.similar:
            similars.add(s.id)
        d = {}
        d["id"] = r.id
        d["title"] = r.title
        d["similar"] = [f"{s.id} {round(s.score, 3)} {s.title}" for s in r.similar]

        dicts.append(d)

    df = pd.DataFrame(dicts)
    df.to_csv(get_similars_path(), index=False)
    return df


df_similar = get_similar_df(0.9)
df_human = get_df_human().reset_index()
df_human["index"] = df_human.apply(lambda r: f"{r['id']}{r['lang']}", axis=1)
df_human.set_index("index", inplace=True)
title_lookup = df_human["title"].to_dict()


def tojson(item: List[str]):
    return [i.split(" ", maxsplit=2) for i in item]


def to_friendly(item: List[str]):
    return "\n".join([" ".join(i) for i in item])


def filter(item: List[str]):
    return [i for i in item if float(i[1]) > 0.98]


def replace_title(id, orig):
    if id in title_lookup:
        return title_lookup[id]
    return f"MISS_{orig}"


def title_replacer(row):
    row["title"] = replace_title(row["id"], row["title"])
    new_similar = []
    for i in row["similar"]:
        id, score, title = i
        new_similar.append([id, score, replace_title(id, title)])
    row["similar"] = new_similar
    return row


def title_filter(row):
    new_similar = []
    for i in row["similar"]:
        id, score, title = i
        if title != row["title"]:
            new_similar.append([id, score, title])
    row["similar"] = new_similar
    return row


df_similar["similar"] = df_similar["similar"].apply(tojson).apply(filter)
dup_filter = df_similar["similar"].apply(lambda x: len(x) > 0)
print(df_similar.shape)
df_similar = df_similar[dup_filter]
print(df_similar)
print(df_similar.shape)
df_similar = df_similar.apply(title_replacer, axis=1)
print(df_similar)
df_similar = df_similar.apply(title_filter, axis=1)
dup_filter = df_similar["similar"].apply(lambda x: len(x) > 0)
df_similar = df_similar[dup_filter]
df_similar["similar"] = df_similar["similar"].apply(to_friendly)
print(df_similar)


df_similar.to_csv(get_filtered_similars_path(), index=False)
