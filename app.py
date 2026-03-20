import streamlit as st
from ytmusicapi import YTMusic
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import certifi

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Musico YT", page_icon="🎵", layout="wide")

# --- 2. DATABASE SETUP ---
@st.cache_resource
def init_db():
    try:
        MONGO_URI = st.secrets["MONGO_URI"]
        client = MongoClient(
            MONGO_URI, 
            server_api=ServerApi('1'), 
            tlsCAFile=certifi.where()
        )
        client.admin.command('ping')
        return client.musico_db 
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        st.stop()

db = init_db()
playlist_col = db.my_playlist

@st.cache_resource
def get_yt(): 
    return YTMusic()

yt = get_yt()

# --- 3. LOAD EXTERNAL CSS ---
def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError: 
        pass

local_css("style.css")

# --- 4. SIDEBAR (LIBRARY) ---
with st.sidebar:
    st.title("📂 My Library")
    
    # Always fetch latest from DB to ensure sync
    saved_songs = list(playlist_col.find())
    
    if not saved_songs:
        st.info("Your library is empty. Save a song to see it here!")
    else:
        for song in saved_songs:
            with st.expander(f"🎵 {song['title']}"):
                st.write(f"**Artist:** {song['artist']}")
                if st.button("Play Now", key=f"lib_p_{song['videoId']}"):
                    st.session_state.search_value = f"{song['title']} {song['artist']}"
                    # Clear current results to force a fresh search for this song
                    st.session_state.results = None
                    st.rerun()
                if st.button("🗑️ Remove", key=f"lib_d_{song['videoId']}"):
                    playlist_col.delete_one({"videoId": song['videoId']})
                    st.rerun()
    
    st.divider()
    if st.button("⚠️ Clear All Data"):
        playlist_col.delete_many({})
        st.rerun()

# --- 5. MAIN INTERFACE ---
st.title("📺 Musico YT")

# INITIALIZE SESSION STATE
if "results" not in st.session_state:
    st.session_state.results = None

triggered_search = st.session_state.get("search_value", "")

with st.form(key='search_form', clear_on_submit=False):
    col_input, col_btn = st.columns([4, 1])
    with col_input:
        search_query = st.text_input(
            "", 
            value=triggered_search, 
            placeholder="🔍 Search for a song or artist...", 
            label_visibility="collapsed"
        )
    with col_btn:
        submit_search = st.form_submit_button("Search", use_container_width=True)

# EXECUTE SEARCH & STORE IN SESSION STATE
if (submit_search or triggered_search) and search_query:
    st.session_state.search_value = "" # Clear the trigger
    with st.spinner("Finding your track..."):
        # Store results so they persist through reruns (like saving)
        st.session_state.results = yt.search(search_query, filter="songs", limit=1)

# DISPLAY RESULTS FROM SESSION STATE
if st.session_state.results:
    track = st.session_state.results[0]
    v_id, title, thumb = track['videoId'], track['title'], track['thumbnails'][-1]['url']
    artist = track['artists'][0]['name']

    with st.container():
        col_img, col_play = st.columns([1, 1.5], gap="large")
        with col_img:
            st.image(thumb, use_container_width=True)
            st.write("")
            
            # CHECK IF SAVED
            is_saved = playlist_col.find_one({"videoId": v_id})
            if is_saved:
                st.button("✅ Saved in Library", disabled=True, use_container_width=True)
            else:
                if st.button("⭐ Save to Library", key=f"save_btn_{v_id}", use_container_width=True):
                    playlist_col.insert_one({
                        "videoId": v_id, 
                        "title": title, 
                        "artist": artist, 
                        "thumb": thumb
                    })
                    st.toast(f"Added {title} to Library!")
                    st.rerun()

        with col_play:
            st.markdown(f"<h1 style='margin-bottom:0;'>{title}</h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#cc0000; font-size:1.3rem; font-weight:600; margin-top:0;'>{artist}</p>", unsafe_allow_html=True)
            st.video(f"https://www.youtube.com/watch?v={v_id}")

    # Recommendations
    st.divider()
    st.subheader("🔥 Recommended Next")
    try:
        suggestions = yt.get_watch_playlist(videoId=v_id, limit=5)['tracks']
        cols = st.columns(4)
        for i, rec in enumerate(suggestions[1:5]):
            with cols[i]:
                img_url = rec['thumbnail'][0]['url']
                rec_artist = rec['artist'][0]['name'] if rec['artist'] else "Unknown"
                
                st.markdown(f"""
                    <div style="height:160px; overflow:hidden; border-radius:15px; margin-bottom:10px; border: 1px solid #efeff3;">
                        <img src="{img_url}" style="width:100%; height:100%; object-fit:cover;">
                    </div>
                """, unsafe_allow_html=True)
                st.write(f"**{rec['title'][:22]}**")
                
                if st.button("Listen", key=f"rec_{rec['videoId']}", use_container_width=True):
                    st.session_state.search_value = f"{rec['title']} {rec_artist}"
                    st.session_state.results = None # Reset for new search
                    st.rerun()
    except: 
        st.info("Recommendations are fetching...")
elif submit_search:
    st.error("No results found. Try again!")