import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit.components.v1 as components
from youtube_search import YoutubeSearch
import pandas as pd
import plotly.express as px
import time

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Musico", page_icon="🎵", layout="wide")

# --- 2. LOAD EXTERNAL CSS ---
def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Could not find {file_name}. Make sure it is in the same folder as app.py")

local_css("style.css")

# --- 3. AUTHENTICATION ---
@st.cache_resource
def get_spotify_client():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id='YOUR_CLIENT_ID_HERE',          # <--- PASTE REAL ID
        client_secret='YOUR_CLIENT_SECRET_HERE',  # <--- PASTE REAL SECRET
        redirect_uri='http://127.0.0.1:8888/callback',
        scope="user-library-read"
    ))

# --- UPDATED FUNCTION: GETS STATS NOW ---
def get_youtube_data(song_name, artist_name):
    query = f"{song_name} {artist_name} official audio"
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        if results:
            video = results[0]
            video_id = video['id']
            link = f"https://www.youtube.com/watch?v={video_id}"
            thumbnail = video['thumbnails'][0]
            
            # Extract stats (Views, Duration, Channel)
            views = video.get('views', 'N/A')
            duration = video.get('duration', 'N/A')
            channel = video.get('channel', 'Unknown Channel')
            
            return link, thumbnail, video_id, views, duration, channel
    except:
        return None, None, None, None, None, None
    return None, None, None, None, None, None

try:
    sp = get_spotify_client()
except:
    st.error("Authentication failed. Check your keys.")
    st.stop()

# --- 4. HERO SECTION ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.title("🎵 Musico")
    st.write("The Universal Music Finder")

# Search Bar
with st.container():
    col_a, col_b, col_c = st.columns([1, 3, 1])
    with col_b:
        with st.form(key='search_form'):
            search_query = st.text_input("", placeholder="🔍 Search for a song", label_visibility="collapsed")
            submit_button = st.form_submit_button(label='Search')

# --- 5. MAIN LOGIC ---
if submit_button and search_query:
    with st.spinner('Searching Spotify & YouTube databases...'):
        time.sleep(1) 
        results = sp.search(q=search_query, type='track', limit=1)
    
    if not results['tracks']['items']:
        st.error("Song not found.")
    else:
        track = results['tracks']['items'][0]
        artist = track['artists'][0]
        
        # Call the new function
        yt_url, yt_thumb, yt_id, yt_views, yt_duration, yt_channel = get_youtube_data(track['name'], artist['name'])

        # TABS LAYOUT
        tab1, tab2, tab3 = st.tabs(["🎧 Player", "📊 Audio Stats", "🔥 Similar Songs"])

        # TAB 1: PLAYER
        with tab1:
            c1, c2 = st.columns([1, 1])
            with c1:
                st.subheader("Spotify Audio")
                st.image(track['album']['images'][0]['url'], width=300)
                st.markdown(f"### {track['name']}")
                st.caption(f"by {artist['name']}")
                components.iframe(f"https://open.spotify.com/embed/track/{track['id']}", height=80)
            
            with c2:
                st.subheader("YouTube Video")
                if yt_url:
                    st.video(yt_url)
                else:
                    st.warning("Video not found")

        # TAB 2: STATS (YouTube + Spotify)
        with tab2:
            st.subheader("📈 Track Statistics")
            
            # 1. Show YouTube Stats First (They always exist!)
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("YouTube Views", yt_views.split(' ')[0] if yt_views else "N/A") # Clean up 'views' text
            col_b.metric("Duration", yt_duration)
            col_c.metric("Channel", yt_channel)
            
            st.divider()

            # 2. Show Spotify Vibe Stats (If available)
            st.subheader("🎵 Spotify Vibe Analysis")
            features = None
            try:
                features = sp.audio_features([track['id']])[0]
            except Exception:
                features = None
            
            if features:
                stats = {
                    'Feature': ['Danceability', 'Energy', 'Valence (Happy)', 'Acousticness'],
                    'Value': [features['danceability'], features['energy'], features['valence'], features['acousticness']]
                }
                df_stats = pd.DataFrame(stats)
                fig = px.bar(df_stats, x='Feature', y='Value', color='Value', 
                             color_continuous_scale='Greens', range_y=[0, 1])
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="white")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("⚠️ Spotify Audio Features (Energy/Danceability) are restricted for this track.")

        # TAB 3: RECOMMENDATIONS
        with tab3:
            st.subheader(f"More from {artist['name']}")
            top_tracks = sp.artist_top_tracks(artist['id'], country='IN')
            cols = st.columns(4)
            for idx, rec in enumerate(top_tracks['tracks'][:4]):
                with cols[idx]:
                    st.image(rec['album']['images'][0]['url'])
                    st.caption(rec['name'])
                    components.iframe(f"https://open.spotify.com/embed/track/{rec['id']}", height=80)