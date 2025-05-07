import requests

API_KEY = "2dc4a6d58d010ecd9ecce214d784eb88"
response = requests.get(f"https://api.the-odds-api.com/v4/sports/?apiKey={API_KEY}")
sports = response.json()
for sport in sports:
    print(f"{sport['key']} - {sport['title']}")
