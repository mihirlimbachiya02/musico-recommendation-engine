import spotipy
from spotipy.oauth2 import SpotifyOAuth

# 1. SETUP: Authenticate with Spotify
# We use the exact Redirect URI you set in the dashboard: http://localhost:8888/callback
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id='71e54fe16f2a45eaadf14ecbbe120dc3',          # <--- PASTE YOUR CLIENT ID
    client_secret='76d2acb5d8d24c89a9e7831fa76b4143',  # <--- PASTE YOUR CLIENT SECRET
    redirect_uri='https://musico.com/callback',
    scope="user-library-read"                 # Permission to read data
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