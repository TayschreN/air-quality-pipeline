import requests, os
from dotenv import load_dotenv
load_dotenv()
key = os.getenv("OPENAQ_API_KEY")
r = requests.get("https://api.openaq.org/v3/countries", headers={"X-API-Key": key}, params={"limit": 200})
for c in r.json()["results"]:
    if "braz" in c["name"].lower():
        print(c["id"], c["code"], c["name"])