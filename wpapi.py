import requests
import time
from ParamsIndexRepo import ParamsIndexRepo, BASE_DIR, get_params_dir

# Reference: https://developer.wordpress.org/rest-api/reference/posts/
BASE_URL="https://2r095.wpdevsite.co"

username="andrew"
password="xTwH tN0f bQHv E8cD 61mx kcZn"
url = BASE_URL + "/wp-json/wp/v2/posts"

# response = requests.get(url, auth=(username, password))
# print(response.text)

visited = ParamsIndexRepo(BASE_DIR, 'visited.json')

for entry in visited.values():
    if entry['action'] == 'list':
        continue
    
    content_dir = get_params_dir(entry)
    with open(f"{content_dir}/content.html", 'r') as f:
        post_content = f.read()

    post_payload = {
        "title": entry['title'],
        "date": "2021-01-01T00:00:00",
        "status": "draft",
        "author": 1,
        "format": "standard",
        "content": post_content,
    }

    response = requests.post(url, auth=(username, password), json=post_payload)
    print(response.text)
    time.sleep(1)

