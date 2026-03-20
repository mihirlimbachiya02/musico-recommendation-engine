# 🎵 Musico YT: The Ultimate YouTube Music Finder

Musico YT is a modern, high-performance web application built with **Streamlit** that allows users to search for any song on YouTube Music, play full videos directly in the browser, and manage a persistent personal library powered by **MongoDB Atlas**.

## 🚀 Features

* **YT Music Engine**: Search for tracks, artists, and albums using the `ytmusicapi`.
* **Integrated Player**: Watch full YouTube videos without leaving the app.
* **Smart Recommendations**: "YouTube Radio" style suggestions based on your current search.
* **Persistent Library**: Save your favorite tracks to a cloud-based **MongoDB** database.
* **Modern UI**: Custom CSS with a "YouTube Dark Mode" aesthetic and glassmorphism effects.
* **Secure Coding**: Credential protection using Streamlit Secrets and `.gitignore` for safe public deployments.

## 🛠️ Tech Stack

* **Frontend**: [Streamlit](https://streamlit.io/)
* **Music API**: [ytmusicapi](https://ytmusicapi.readthedocs.io/)
* **Database**: [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
* **Data Visualization**: [Plotly](https://plotly.com/python/) & [Pandas](https://pandas.pydata.org/)
* **Styling**: Custom CSS (External)

## 📂 Project Structure

```text
Musico/
├── .streamlit/
│   └── secrets.toml      # Local storage for MongoDB URI (Hidden)
├── app.py                # Main Application Logic
├── style.css             # Custom YouTube Dark Mode Theme
├── requirements.txt      # Project Dependencies
└── .gitignore            # Prevents sensitive files from being pushed to GitHub