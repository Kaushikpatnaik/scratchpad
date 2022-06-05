import requests

payload = {"url": "https://www.youtube.com/watch?v=71-l49nRGK0"}

url = "https://us-west2-scratchpad-348314.cloudfunctions.net/yt_parser"

r = requests.post(url, data=payload)
print("Status Code ", r.status_code)