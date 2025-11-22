# 🎵 Musico Recommendation Engine

A music recommendation app built with Python and the Spotify API.
It suggests songs based on your favorite tracks and provides audio analysis charts.

## Features
- 🎧 Search for any song
- 📊 View Audio Analysis (Energy vs. Danceability)
- ▶️ Listen to song previews directly in the app
- 🎨 Clean interface built with Streamlit

## How to Run Locally
1. Clone this repository
2. Install requirements:
   `pip install -r requirements.txt`
3. Create a Spotify App at [developer.spotify.com](https://developer.spotify.com)
   - Set Redirect URI to: `http://127.0.0.1:8888/callback`
4. Add your Client ID and Secret to `app.py`
5. Run the app:
   `streamlit run app.py`

