from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from joblib import Parallel, delayed
from operator import itemgetter
from ParamsIndexRepo import ParamsIndexRepo, BASE_DIR, get_html_path, get_similars_path

import pandas as pd
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class Similar:
    id: int
    title: str
    score: float


@dataclass
class Record:
    id: int
    title: str
    content: str
    similar: List[Similar]


def get_post(post) -> Optional[Record]:
    id, title = itemgetter("id", "title")(post)
    action = post["action"] if "action" in post else None
    if action == "list":
        return None
    lang = post["lang"] if "lang" in post else "none"
    path_original = get_html_path(id, lang, title)
    with open(path_original, "r") as f:
        content = f.read()

    return Record(id, title, content, [])


visited = ParamsIndexRepo(BASE_DIR, "visited.json")
posts = visited.unique_href_values()

records: List[Record] = [p for p in [get_post(p) for p in posts] if p]
# records = records[0:1000]

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

THRESHOLD = 0.9


idx = 0
for i in range(len(records)):
    r = records[i]
    for j in range(i + 1, len(records)):
        s = records[j]
        score = similarities[idx]
        if score >= THRESHOLD:
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
    d["similar"] = "\n".join(
        [f"{s.id} {round(s.score, 3)} {s.title}" for s in r.similar]
    )
    dicts.append(d)

df = pd.DataFrame(dicts)
print(df)
df.to_csv(get_similars_path())
