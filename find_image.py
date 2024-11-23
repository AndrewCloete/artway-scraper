import ast
import asyncio
import aiohttp
from ParamsIndexRepo import (
    get_wpallimport_path,
)
import pandas as pd

df: pd.DataFrame = pd.read_csv(get_wpallimport_path("clean"))


# img_cols = [c for c in df.columns if "image" in c]
# num_cols = [c.split("_")[1] for c in img_cols]
# for col in img_cols:
#     (_, num) = col.split("_")
#     df[num] = df[col].str.contains(r"\s", na=False)


def blanks(urls_str):
    urls = ast.literal_eval(urls_str)
    out = ""
    i = 0
    for url in urls:
        if " " in url.strip():
            out += str(i) + "|"
        i += 1
    return out


def blank_urls(urls_str):
    urls = ast.literal_eval(urls_str)
    return [url for url in urls if " " in url.strip()]


def fix_urls(urls_str):
    urls = ast.literal_eval(urls_str)
    return [url.replace(" ", "%20") for url in urls if " " in url.strip()]


async def check_url(session, url):
    """Check if a single URL exists."""
    try:
        async with session.head(url, allow_redirects=True, timeout=5) as response:
            return url, response.status == 200
    except Exception:
        return url, False


async def check_urls_in_batches(urls):
    """Check a list of URLs in batches."""
    batch_size = 100
    results = []
    async with aiohttp.ClientSession() as session:
        for i in range(0, len(urls), batch_size):
            batch = urls[i : i + batch_size]
            print(batch)
            tasks = [check_url(session, url) for url in batch]
            results.extend(await asyncio.gather(*tasks))
    return results


df["blanks"] = df["image_urls"].apply(blanks)
df["culprits"] = df["image_urls"].apply(blank_urls)
df["fixed"] = df["image_urls"].apply(fix_urls)
df[["id", "real_lang", "title", "blanks", "culprits", "fixed"]].to_csv(
    "/tmp/image_urls_with_space.csv", index=False
)

loop = asyncio.get_event_loop()
results = loop.run_until_complete(
    check_urls_in_batches([url for urls in list(df["fixed"]) for url in urls])
)
for url, exists in results:
    if not exists:
        print(f"{url} exists: {exists}")
