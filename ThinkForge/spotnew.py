import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
import sys
from datetime import datetime, timedelta

class SpotifyTrending:
    def __init__(self):
        self.sp = self.authenticate_spotify()
        
    def authenticate_spotify(self):
        """Authenticate with Spotify API using credentials from .env file"""
        if not load_dotenv():
            print("Error: .env file not found in the current directory.")
            print("Please create a .env file with your Spotify credentials:")
            print("SPOTIFY_CLIENT_ID=your_client_id_here")
            print("SPOTIFY_CLIENT_SECRET=your_client_secret_here")
            return None

        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

        if not client_id or not client_secret:
            print("Error: Spotify credentials not found in .env file.")
            print("Please make sure your .env file contains:")
            print("SPOTIFY_CLIENT_ID=your_client_id_here")
            print("SPOTIFY_CLIENT_SECRET=your_client_secret_here")
            return None

        try:
            auth_manager = SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
            return spotipy.Spotify(auth_manager=auth_manager)
        except Exception as e:
            print(f"Authentication failed: {e}")
            print("Make sure your Spotify credentials in the .env file are correct.")
            return None

    def get_playlist_tracks(self, playlist_id, limit=50):
        """Fetch tracks from a specific playlist"""
        try:
            tracks = []
            results = self.sp.playlist_tracks(
                playlist_id,
                fields='items(added_at,track(name,id,artists,album,popularity))',
                limit=limit
            )
            
            for item in results['items']:
                if item['track']:
                    track = item['track']
                    tracks.append({
                        'name': track['name'],
                        'artist': ', '.join(artist['name'] for artist in track['artists']),
                        'album': track['album']['name'],
                    })
            return tracks
        except Exception as e:
            print(f"Error fetching playlist {playlist_id}: {e}")
            return []

    def get_trending_songs(self, limit=10):
        """Get trending songs from various sources"""
        all_tracks = []
        
        # Primary playlist (Latest Trending)
        primary_playlist_id = "1saCqPsl314giXN0GLWgLj"
        print("Fetching latest trending tracks...")
        primary_tracks = self.get_playlist_tracks(primary_playlist_id, limit)
        all_tracks.extend(primary_tracks)

        # Additional playlists to check
        playlist_ids = [
            "37i9dQZEVXbLZ52XmnySJg",  # Top 50 India
            "37i9dQZF1DX1jGsxSsUe76",  # Bollywood Butter
            "37i9dQZF1DWTtTyktzRQEm"   # Hot Hits Hindi
        ]

        if len(all_tracks) < limit:
            for playlist_id in playlist_ids:
                if len(all_tracks) >= limit:
                    break
                tracks = self.get_playlist_tracks(playlist_id, limit)
                for track in tracks:
                    if not any(t['name'] == track['name'] and t['artist'] == track['artist'] 
                            for t in all_tracks):
                        all_tracks.append(track)
        
        # Remove added_at before returning
        for track in all_tracks:
            track.pop('added_at', None)
            
        return all_tracks[:limit]

    def display_trending_songs(self, songs):
        """Display the trending songs in a formatted way"""
        if not songs:
            print("No trending songs found.")
            return

        print("\n" + "="*60)
        print(" "*20 + "CURRENT TRENDING SONGS IN INDIA")
        print("="*60)

        for i, song in enumerate(songs, 1):
            print(f"\n{i}. Song: {song['name']}")
            print(f"   Artist: {song['artist']}")
            print(f"   Album: {song['album']}")
            print(f"   Popularity: {song['popularity']}")
            print("-"*60)

def main():
    print("Initializing Spotify Trending Songs India...")
    
    try:
        import dotenv
    except ImportError:
        print("Error: python-dotenv package is not installed.")
        print("Please install it using: pip install python-dotenv")
        return

    spotify = SpotifyTrending()
    if not spotify.sp:
        return

    try:
        trending_songs = spotify.get_trending_songs()
        spotify.display_trending_songs(trending_songs)
    except Exception as e:
        print(f"Error fetching trending songs: {e}")
        print("Please check your internet connection and Spotify credentials.")

if __name__ == "__main__":
    main()

