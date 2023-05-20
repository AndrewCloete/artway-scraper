import requests

BASE_URL="https://2r095.wpdevsite.co"

username="Otto"
password="Tw8D@ZY2hbyTeWh"
# url = BASE_URL + "/wp-json"
url = BASE_URL + "/wp-json/wp/v2/posts/1"

response = requests.get(url, auth=(username, password))
print(response.text)
