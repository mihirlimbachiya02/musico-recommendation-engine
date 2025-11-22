import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit.components.v1 as components
from youtube_search import YoutubeSearch # The new magic tool

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Musico", page_icon="🎵", layout="wide")

# Custom CSS for cool buttons
st.markdown("""
<style>
    .stButton button {
        width: 100%;
        border-radius: 5px;
    }
    .stTextInput > div > div > input {
        font-size: 20px; padding: 12px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. AUTHENTICATION ---
@st.cache_resource
def get_spotify_client():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id='YOUR_CLIENT_ID_HERE',          # <--- PASTE ID
        client_secret='YOUR_CLIENT_SECRET_HERE',  # <--- PASTE SECRET
        redirect_uri='http://127.0.0.1:8888/callback',
        scope="user-library-read"
    ))

# --- 3. NEW HELPER FUNCTIONS ---
def get_youtube_link(song_name, artist_name):
    """Searches YouTube and returns the first video URL and Thumbnail"""
    query = f"{song_name} {artist_name} official audio"
    try:
        # Search YouTube
        results = YoutubeSearch(query, max_results=1).to_dict()
        if results:
            video_id = results[0]['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            thumbnail = results[0]['thumbnails'][0]
            return video_url, thumbnail, video_id
    except:
        return None, None, None
    return None, None, None

def make_clickable_link(url, text):
    return f'<a href="{url}" target="_blank" style="text-decoration:none; color:#1DB954; font-weight:bold;">{text}</a>'

try:
    sp = get_spotify_client()
except:
    st.error("Authentication failed. Check your keys.")
    st.stop()

# --- 4. HERO SECTION ---
st.title("🎵 Musico")
st.write("Search once, listen everywhere (Spotify, YouTube, Apple Music).")

with st.form(key='search_form'):
    col1, col2 = st.columns([4, 1])
    with col1:
        search_query = st.text_input("Search for a song...", placeholder="e.g., O Re Piya")
    with col2:
        st.write("")
        st.write("")
        submit_button = st.form_submit_button(label='🔍 Find')

# --- 5. RESULTS ---
if submit_button and search_query:
    # A. Search Spotify
    results = sp.search(q=search_query, type='track', limit=1)
    
    if not results['tracks']['items']:
        st.error("Song not found on Spotify.")
    else:
        track = results['tracks']['items'][0]
        artist = track['artists'][0]
        track_name = track['name']
        artist_name = artist['name']

        # B. Search YouTube (The new part)
        yt_url, yt_thumb, yt_id = get_youtube_link(track_name, artist_name)
        
        st.divider()
        
        # --- LAYOUT: 2 Columns ---
        col_left, col_right = st.columns([1, 1])
        
        # LEFT: Spotify Player
        with col_left:
            st.subheader("🎧 Spotify")
            st.image(track['album']['images'][0]['url'], width=300)
            st.markdown(f"### {track_name}")
            st.markdown(f"**{artist_name}**")
            
            # Spotify Embed
            components.iframe(f"https://open.spotify.com/embed/track/{track['id']}", height=80)
            
            # External Links
            st.markdown("##### 🔗 Open on other apps:")
            # We generate "Smart Search Links"
            yt_music_url = f"https://music.youtube.com/search?q={track_name}+{artist_name}"
            apple_url = f"https://music.apple.com/us/search?term={track_name}+{artist_name}"
            
            c1, c2 = st.columns(2)
            c1.markdown(f"[🔴 YouTube Music]({yt_music_url})")
            c2.markdown(f"[🍎 Apple Music]({apple_url})")

        # RIGHT: YouTube Video Player
        with col_right:
            st.subheader("📺 YouTube Video")
            if yt_url:
                # Native Streamlit Video Player
                st.video(yt_url)
            else:
                st.warning("Could not find video on YouTube.")

        # --- C. RECOMMENDATIONS ---
        st.divider()
        st.subheader(f"🔥 More like {artist_name}")
        
        top_tracks = sp.artist_top_tracks(artist['id'], country='IN')
        
        # Grid of 3
        cols = st.columns(3)
        for idx, rec_track in enumerate(top_tracks['tracks'][:3]):
            with cols[idx]:
                st.image(rec_track['album']['images'][0]['url'])
                st.write(f"**{rec_track['name']}**")
                # Smart Link for recommendations too
                search_q = f"{rec_track['name']} {rec_track['artists'][0]['name']}"
                yt_search = f"https://www.youtube.com/results?search_query={search_q}"
                st.markdown(f"[▶ Watch on YouTube]({yt_search})")