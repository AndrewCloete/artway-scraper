import pandas as pd

from ParamsIndexRepo import ParamsIndexRepo, BASE_DIR

visited = ParamsIndexRepo(BASE_DIR, 'visited.json')

df = pd.DataFrame(visited.values())
df['image_count'] = df['image_urls'].apply(len)

df.to_csv('/tmp/artway_index.csv', index=False)
