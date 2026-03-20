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
    st.markdown("# 📂 My Library")
    
    # FETCH SONGS: Pull fresh data every rerun
    saved_songs = list(playlist_col.find())
    
    if "current_track" in st.session_state:
        st.markdown("---")
        st.caption("🎧 NOW PLAYING")
        st.info(f"**{st.session_state.current_track}**")
    
    st.markdown("---")
    
    if not saved_songs:
        st.info("Your library is empty.")
    else:
        for song in saved_songs:
            with st.expander(f"🎶 {song['title'][:20]}..."):
                st.write(f"👤 **Artist:** {song['artist']}")
                col_p, col_d = st.columns(2)
                with col_p:
                    if st.button("▶️ Play", key=f"lib_p_{song['videoId']}"):
                        st.session_state.search_value = f"{song['title']} {song['artist']}"
                        st.session_state.current_track = song['title']
                        st.rerun()
                with col_d:
                    if st.button("🗑️ Del", key=f"lib_d_{song['videoId']}"):
                        playlist_col.delete_one({"videoId": song['videoId']})
                        st.rerun()
    
    st.markdown("---")
    if st.button("⚠️ Clear All Data", use_container_width=True):
        playlist_col.delete_many({})
        if "current_track" in st.session_state:
            del st.session_state.current_track
        st.rerun()

# --- 5. MAIN INTERFACE ---
st.markdown("<h1>📺 Musico YT</h1>", unsafe_allow_html=True)

triggered_search = st.session_state.get("search_value", "")

with st.form(key='search_form', clear_on_submit=False):
    col_input, col_btn = st.columns([4, 1])
    with col_input:
        search_query = st.text_input(
            "Search", 
            value=triggered_search, 
            placeholder="🔍 Search for a song or artist...", 
            label_visibility="collapsed"
        )
    with col_btn:
        submit_search = st.form_submit_button("Search", use_container_width=True)

# EXECUTE SEARCH
if (submit_search or triggered_search) and search_query:
    st.session_state.search_value = "" 
    
    with st.spinner("Finding your track..."):
        results = yt.search(search_query, filter="songs", limit=1)
    
    if results:
        track = results[0]
        v_id, title, thumb = track['videoId'], track['title'], track['thumbnails'][-1]['url']
        artist = track['artists'][0]['name']

        with st.container():
            col_img, col_play = st.columns([1, 1.5], gap="large")
            
            with col_img:
                st.image(thumb, use_container_width=True)
                st.write("")
                
                # RE-FIXED LOGIC: Everything nested correctly under col_img
                is_saved = playlist_col.find_one({"videoId": v_id})
                
                if is_saved:
                    st.button("✅ Already in Library", disabled=True, use_container_width=True)
                else:
                    if st.button("⭐ Save to Library", key=f"save_{v_id}", use_container_width=True):
                        try:
                            playlist_col.insert_one({
                                "videoId": v_id, 
                                "title": title, 
                                "artist": artist, 
                                "thumb": thumb
                            })
                            st.toast(f"Saved {title}!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

            with col_play:
                st.markdown(f"<h2>{title}</h2>", unsafe_allow_html=True)
                st.markdown(f"""
                    <p style='background: linear-gradient(90deg, #ff4d4d, #8a2be2); 
                                -webkit-background-clip: text; 
                                -webkit-text-fill-color: transparent; 
                                font-size:1.4rem; font-weight:700; margin-top:0;'>
                        {artist}
                    </p>
                """, unsafe_allow_html=True)
                st.video(f"https://www.youtube.com/watch?v={v_id}")

        st.divider()
        st.subheader("🔥 Recommended Next")
        try:
            suggestions = yt.get_watch_playlist(videoId=v_id, limit=5)['tracks']
            cols = st.columns(4)
            for i, rec in enumerate(suggestions[1:5]):
                with cols[i]:
                    img_url = rec['thumbnail'][0]['url']
                    rec_artist = rec['artist'][0]['name'] if rec['artist'] else "Unknown"
                    st.markdown(f'<div style="height:160px; overflow:hidden; border-radius:15px; margin-bottom:10px;"><img src="{img_url}" style="width:100%; height:100%; object-fit:cover;"></div>', unsafe_allow_html=True)
                    st.write(f"**{rec['title'][:22]}**")
                    if st.button("Listen", key=f"rec_{rec['videoId']}", use_container_width=True):
                        st.session_state.search_value = f"{rec['title']} {rec_artist}"
                        st.rerun()
        except: 
            pass
    else: 
        st.error("No results found.")