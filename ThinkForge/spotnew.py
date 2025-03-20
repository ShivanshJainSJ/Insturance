import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
import sys
from datetime import datetime, timedelta
import pygame
import urllib.request
import tempfile
import time

class SpotifyTrending:
    def __init__(self):
        self.sp = self.authenticate_spotify()
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        
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
                fields='items(added_at,track(name,id,artists,album,popularity,preview_url,uri))',
                limit=limit
            )
            
            for item in results['items']:
                if item['track']:
                    track = item['track']
                    tracks.append({
                        'name': track['name'],
                        'artist': ', '.join(artist['name'] for artist in track['artists']),
                        'album': track['album']['name'],
                        'preview_url': track.get('preview_url'),
                        'uri': track.get('uri'),
                        'popularity': track.get('popularity', 0)
                    })
            return tracks
        except Exception as e:
            print(f"Error fetching playlist {playlist_id}: {e}")
            return []
    def play_song(self, preview_url):
        """Play a song preview using pygame mixer"""
        if not preview_url:
            print("No preview URL available for this track.")
            return False
        
        try:
            print("Downloading preview...")
            # Create a temporary file to store the preview
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_file.close()
            
            # Download the preview
            urllib.request.urlretrieve(preview_url, temp_file.name)
            
            # Load and play the preview
            print("Playing preview... (Press Ctrl+C to stop)")
            pygame.mixer.music.load(temp_file.name)
            pygame.mixer.music.play()
            
            # Play for up to 30 seconds (or until the preview ends)
            start_time = time.time()
            try:
                while pygame.mixer.music.get_busy() and (time.time() - start_time < 30):
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopping playback...")
            finally:
                pygame.mixer.music.stop()
                # Clean up the temporary file
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
            
            return True
        except Exception as e:
            print(f"Error playing track: {e}")
            return False

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
            # Make sure all tracks have popularity field
            if 'popularity' not in track:
                track['popularity'] = 0
            
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
            print(f"   Popularity: {song.get('popularity', 'N/A')}")
            if song.get('preview_url'):
                print(f"   Preview Available: Yes")
            else:
                print(f"   Preview Available: No")
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
                    if 0 <= index < len(trending_songs):
                        selected_song = trending_songs[index]
                        print(f"\nPlaying preview for: {selected_song['name']} by {selected_song['artist']}")
                        
                        if not spotify.play_song(selected_song.get('preview_url')):
                            print("No preview available or playback error. Try another song.")
                    else:
                        print("Invalid selection. Please enter a valid number.")
                except ValueError:
                    print("Please enter a valid number or 'q' to quit.")
    except Exception as e:
        print(f"Error fetching trending songs: {e}")
        print("Please check your internet connection and Spotify credentials.")

if __name__ == "__main__":
    main()

