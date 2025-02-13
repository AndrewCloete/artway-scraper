import pandas as pd
from bs4 import BeautifulSoup


def find_first_image(html):
    if html != html:
        return "no html"

    soup = BeautifulSoup(html, "html.parser")
    images = soup.find_all("img")
    if len(images) < 1:
        return "no images"
    return images[0]["src"]


def clean_image_col(image: str):
    if image.startswith("no"):
        return None
    return image


def image_status(image: str):
    if image.startswith("no"):
        return image
    return "has image"


LANG = "nl"
df = pd.read_csv(f"/tmp/wf_export_{LANG}.csv")

df["Thumbnails"] = df["Post Content"].apply(find_first_image)
df["Thumbnail"] = df["Thumbnails"].apply(clean_image_col)
df["Image status"] = df["Thumbnails"].apply(image_status)

df.to_csv("data/wf_export_en_out.csv")
df[["Name", "Slug", "Item ID", "Image status", "Thumbnail"]].to_csv(
    f"/tmp/wf_export_{LANG}_out_small.csv"
)
