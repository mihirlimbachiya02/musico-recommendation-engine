# 🎵 Musico 

**Search once, listen everywhere.**
Musico is a smart music recommendation engine that bridges the gap between Spotify and YouTube. It allows you to search for songs via Spotify's powerful metadata and instantly watch the corresponding music video on YouTube without ads or login.

## ✨ Features
- **Dual-Platform Integration:** Search on Spotify, Watch on YouTube.
- **Embedded Player:** Play 30s audio previews (Spotify) or full music videos (YouTube) directly in the app.
- **Smart Links:** Auto-generates search links for **Apple Music** and **YouTube Music**.
- **Recommendation Engine:** Suggests similar tracks based on Artist algorithms.
- **Clean UI:** Built with Streamlit for a responsive, dark-mode interface.

## 🛠️ Tech Stack
- **Python 3.x**
- **Streamlit** (Frontend)
- **Spotipy** (Spotify API Client)
- **Youtube-Search** (Video Scraper)

## How to Run Locally
1. Clone this repository
2. Install requirements:
   `pip install -r requirements.txt`
3. Create a Spotify App at [developer.spotify.com](https://developer.spotify.com)
   - Set Redirect URI to: `http://127.0.0.1:8888/callback`
4. Add your Client ID and Secret to `app.py`
5. Run the app:
   `streamlit run app.py`

