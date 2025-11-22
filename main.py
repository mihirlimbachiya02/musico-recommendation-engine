import spotipy
from spotipy.oauth2 import SpotifyOAuth

# We use the exact Redirect URI you set in the dashboard: http://localhost:8888/callback
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id='YOUR_CLIENT_ID_HERE',          # <--- User must paste their own ID
        client_secret='YOUR_CLIENT_SECRET_HERE',  # <--- User must paste their own Secret
        redirect_uri='http://127.0.0.1:8888/callback',
        scope="user-library-read"
    ))

print("Successfully connected to Spotify!")

def get_recommendations(song_name):
    # 1. SEARCH
    print(f"Searching for '{song_name}'...")
    results = sp.search(q=song_name, type='track', limit=1)
    
    if not results['tracks']['items']:
        print("Song not found.")
        return

    # Get Artist details
    track = results['tracks']['items'][0]
    artist = track['artists'][0]
    artist_id = artist['id']
    artist_name = artist['name']
    
    print(f"Found: {track['name']} by {artist_name}")

    # 2. GET TOP TRACKS (The reliable fix)
    print(f"\n--- Best Songs by {artist_name} ---")
    
    # We ask for the artist's top tracks in India ('IN')
    top_tracks = sp.artist_top_tracks(artist_id, country='IN')
    
    for idx, track in enumerate(top_tracks['tracks'][:5]): # Show top 5
        print(f"{idx+1}. {track['name']}")
        
# 4. RUN: Ask user for input
user_song = input("Enter a song you like: ")
get_recommendations(user_song)