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
import pygame
import time
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
    from datetime import datetime

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
    
    formatted_news = []
    for item in news_items:
        # Format the published date
        published_at = item.get('published_at', '')
        try:
            if published_at:
                date_obj = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%S%z')
                formatted_date = date_obj.strftime('%B %d, %Y at %I:%M %p')
            else:
                formatted_date = 'Date unavailable'
        except ValueError:
            formatted_date = published_at  # Use as is if parsing fails
        
        # Create a formatted news item with more details
        news_detail = {
            'title': item.get('title', 'No title available'),
            'description': item.get('description', 'No description available'),
            'source': item.get('source', 'Unknown source'),
            'published_at': formatted_date,
            'url': item.get('url', '')
        }
        formatted_news.append(news_detail)
    
    return formatted_news



# Function to fetch trending memes
def get_trending_memes():
    """Fetch the top 10 trending memes from imgflip API"""
    response = requests.get(MEMES_API)
    memes = response.json().get("data", {}).get("memes", [])
    # Limit to 10 memes only
    memes = memes[:10]
    meme_details = [{"name": meme["name"], "url": meme["url"], "id": meme["id"]} for meme in memes]
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
            news_items = get_trending_news()
            print("\n" + "="*80 + "\n" + "📰 TRENDING NEWS 📰".center(80) + "\n" + "="*80)
            
            for idx, news in enumerate(news_items, start=1):
                print(f"\n{idx}. {news['title']}")
                print(f"   Source: {news['source']}")
                print(f"   Published: {news['published_at']}")
                print("   " + "-"*70)
                print(f"   {news['description']}")
                if news['url']:
                    print(f"   Link: {news['url']}")
                print("   " + "-"*70)
            
            print("\n" + "="*80 + "\n")
        elif user_input == "trending songs":
            print("Fetching trending songs...")
            spotify = SpotifyTrending()
            songs = spotify.get_trending_songs()
            for idx, song in enumerate(songs, start=1):
                print(f"Song {idx}:")
                print(f"  Name: {song['name']}")
                print(f"  Artist: {song['artist']}")
                print(f"  Album: {song['album']}")
                print(f"  Preview Available: {'Yes' if song.get('preview_url') else 'No'}")
                print("-" * 40)
                
            # Add song playback functionality
            print("\nWould you like to play a preview of any song? (y/n)")
            choice = input().strip().lower()
            if choice == 'y':
                while True:
                    print("\nEnter the number of the song to play (or 'q' to quit):")
                    selection = input().strip()
                    if selection.lower() == 'q':
                        break
                    
                    try:
                        index = int(selection) - 1
                        if 0 <= index < len(songs):
                            selected_song = songs[index]
                            print(f"\nPlaying preview for: {selected_song['name']} by {selected_song['artist']}")
                            
                            if not spotify.play_song(selected_song.get('preview_url')):
                                print("No preview available or playback error. Try another song.")
                        else:
                            print("Invalid selection. Please enter a valid number.")
                    except ValueError:
                        print("Please enter a valid number or 'q' to quit.")
                    except KeyboardInterrupt:
                        print("\nPlayback stopped.")
                        continue

        elif user_input == "trending memes":
            print("Fetching trending memes...")
            memes = get_trending_memes()
            print("\n" + "="*80)
            print("\U0001F602 TOP 10 TRENDING MEMES \U0001F602".center(80))
            print("="*80)
            
            # Display all memes first with better formatting
            for idx, meme in enumerate(memes, start=1):
                print(f"\n{idx}. {meme['name']}")
                print("   " + "-"*70)
                print(f"   ID: {meme['id']}")
                print(f"   URL: {meme['url']}")
                print("   " + "-"*70)
            
            # After displaying all memes, allow selection
            print("\n" + "="*80)
            print("MEME VIEWER OPTIONS".center(80))
            print("="*80)
            print("Enter a number (1-10) to view that meme")
            print("Type 'q' at any time to quit")
            print("-"*80)
            
            while True:
                choice = input("\nEnter meme number or 'q' to quit: ").strip().lower()
                if choice == 'q':
                    break
                
                try:
                    meme_idx = int(choice) - 1
                    if 0 <= meme_idx < len(memes):
                        selected_meme = memes[meme_idx]
                        print(f"\nViewing: {selected_meme['name']}")
                        print("-"*80)
                        
                        try:
                            response = requests.get(selected_meme['url'])
                            img = Image.open(BytesIO(response.content))
                            img.show()
                            print("Opening meme in image viewer...")
                        except Exception as e:
                            print(f"Error opening image: {e}")
                    else:
                        print(f"Please enter a number between 1 and {len(memes)}")
                except ValueError:
                    if choice != 'q':
                        print("Please enter a valid number or 'q' to quit")
            
            print("\n" + "="*80 + "\n")
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