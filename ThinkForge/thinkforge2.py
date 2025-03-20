import requests
import json
from dotenv import load_dotenv
import os
import base64
from bs4 import BeautifulSoup
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI as Gemini
from langchain.prompts import PromptTemplate
import pandas as pd
from PIL import Image
from io import BytesIO
from requests import post
from spotnew import SpotifyTrending

# Load environment variables from .env file
load_dotenv()

# Define API endpoints and keys
NEWS_API = "https://api.mediastack.com/newsRunAPIRequest?access_key=114a71bf4eee701bcce106bb45d7ee39&country=in"
EVENTS_API = "https://app.ticketmaster.com/discovery/v2/events.json"  # Ticketmaster API endpoint
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API = "https://api.spotify.com/v1/browse/new-releases"
MEMES_API = "https://api.imgflip.com/get_memes"

# Get API keys from environment variables
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
EVENTS_API_KEY = os.getenv("EVENTS_API_KEY")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")





# Function to fetch trending searches using web scraping
def get_trending_searches():
    url = "https://trends.google.com/trending/rss?geo=IN"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        # Add logic to parse and return trending searches
    else:
        print("Failed to fetch trending searches")
        return []

# Function to fetch trending news
def get_trending_news():
    import http.client, urllib.parse

    conn = http.client.HTTPConnection('api.mediastack.com')

    params = urllib.parse.urlencode({
        'access_key': '114a71bf4eee701bcce106bb45d7ee39',
        'country': 'india',
        'limit': 10,
        })

    conn.request('GET', '/v1/news?{}'.format(params))

    res = conn.getresponse()
    data = res.read().decode('utf-8')
    news_items = json.loads(data).get('data', [])
    titles = [item['title'] for item in news_items]
    return titles



# Function to fetch trending memes
def get_trending_memes():
    response = requests.get(MEMES_API)
    memes = response.json().get("data", {}).get("memes", [])
    meme_details = [{"name": meme["name"], "url": meme["url"]} for meme in memes]
    return meme_details

# Function to fetch events using Ticketmaster API
def get_events():
    params = {
        "apikey": os.getenv('EVENTS_API_KEY'),
        "countryCode": "IN",
        "classificationName": "music,sports,other,festival",
        "size": 5,
        "sort": "date,asc"
    }
    response = requests.get(EVENTS_API, params=params)
    
    events_data = response.json().get("_embedded", {}).get("events", [])
    events = [{
            "name": event["name"], 
            "start": event["dates"]["start"]["dateTime"],
            "location": event["_embedded"]["venues"][0]["name"]
        } for event in events_data]
    return events

# Initialize the LLM
llm = Gemini(api_key=GEMINI_API_KEY, model="gemini-1.5-flash")

# Define a prompt template
prompt_template = PromptTemplate(input_variables=["input"], template="{input}")

# Create an LLM chain
chain = LLMChain(prompt=prompt_template, llm=llm)

# CLI interface
def main():
    print("Welcome to ThinkForge Chatbot!")
    print("Type 'exit' to quit.")
    while True:
        user_input = input("You: ").strip().lower()
        if user_input == "exit":
            break
        elif user_input == "trending searches":
            print("Fetching trending searches...")
            trending_searches = get_trending_searches()
            print(json.dumps(trending_searches, indent=2))
        elif user_input == "trending news":
            print("Fetching trending news...")
            print(json.dumps(get_trending_news(), indent=2))
        elif user_input == "trending songs":
            print("Fetching trending songs...")
            spotify = SpotifyTrending()
            songs = spotify.get_trending_songs()
            for idx, song in enumerate(songs, start=1):
                print(f"Song {idx}:")
                print(f"  Name: {song['name']}")
                print(f"  Artist: {song['artist']}")
                print(f"  Album: {song['album']}")
                print("-" * 40)

        elif user_input == "trending memes":
            print("Fetching trending memes...")
            memes = get_trending_memes()
            for meme in memes:
                print(f"Name: {meme['name']}")
                print(f"URL: {meme['url']}")
                response = requests.get(meme['url'])
                img = Image.open(BytesIO(response.content))
                img.show()
        elif user_input == "trending events":
            print("Fetching events...")
            events = get_events()
            for idx, event in enumerate(events, start=1):
                print(f"Event {idx}:")
                print(f"  Name: {event['name']}")
                print(f"  Start: {event['start']}")
                print(f"  Location: {event['location']}")
                print("-" * 40)
        else:
            response = chain.run({"input": user_input})
            print(f"ThinkForge: {response}")

if __name__ == "__main__":
    main()