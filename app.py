import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit.components.v1 as components # Required for the Player

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Musico Pro", page_icon="🎧", layout="wide")

# Custom CSS to make the search bar look better
st.markdown("""
<style>
    .stTextInput > div > div > input {
        font-size: 20px;
        padding: 12px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. AUTHENTICATION ---
@st.cache_resource
# Inside app.py
def get_spotify_client():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id='YOUR_CLIENT_ID_HERE',          # <--- User must paste their own ID
        client_secret='YOUR_CLIENT_SECRET_HERE',  # <--- User must paste their own Secret
        redirect_uri='http://127.0.0.1:8888/callback',
        scope="user-library-read"
    ))

try:
    sp = get_spotify_client()
except:
    st.error("Authentication failed. Check your keys.")
    st.stop()

# --- 3. HERO SECTION & SEARCH BAR ---
st.title("🎧 Musico")
st.write("Search for your favorite song to get recommendations and listen instantly.")

# We use a FORM so you can press 'Enter' to search
with st.form(key='search_form'):
    col1, col2 = st.columns([4, 1])
    with col1:
        # A large, clear search bar
        search_query = st.text_input("Search for a song...", placeholder="e.g., Mann Ki Lagan")
    with col2:
        # Align the button with the text box
        st.write("") # Spacer
        st.write("") # Spacer
        submit_button = st.form_submit_button(label='🔍 Search')

# --- 4. MAIN APP LOGIC ---
if submit_button and search_query:
    # A. Search for the song
    results = sp.search(q=search_query, type='track', limit=1)
    
    if not results['tracks']['items']:
        st.error("Song not found. Please try a different spelling.")
    else:
        track = results['tracks']['items'][0]
        artist = track['artists'][0]
        
        # --- B. DISPLAY SEED SONG (With Player) ---
        st.divider()
        st.subheader("🎶 You Selected")
        
        col_img, col_info = st.columns([1, 3])
        with col_img:
            st.image(track['album']['images'][0]['url'], width=200)
        with col_info:
            st.markdown(f"### {track['name']}")
            st.markdown(f"**Artist:** {artist['name']}")
            # EMBED PLAYER: This creates the Spotify Play button
            track_id = track['id']
            components.iframe(f"https://open.spotify.com/embed/track/{track_id}", height=80)

        # --- C. RECOMMENDATIONS (With Players) ---
        st.divider()
        st.subheader(f"🔥 More like {artist['name']}")
        
        # Get Top Tracks by Artist
        top_tracks = sp.artist_top_tracks(artist['id'], country='IN')
        
        # Display in a grid
        cols = st.columns(3) # 3 songs per row
        
        for idx, rec_track in enumerate(top_tracks['tracks'][:6]): # Show top 6
            col = cols[idx % 3] # Cycle through columns
            with col:
                # Show tiny image
                st.image(rec_track['album']['images'][0]['url'], width=100)
                st.write(f"**{rec_track['name']}**")
                # Mini Player for every recommendation
                rec_id = rec_track['id']
                components.iframe(f"https://open.spotify.com/embed/track/{rec_id}", height=80)