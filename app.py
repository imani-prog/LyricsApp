from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import base64
import os
from dotenv import load_dotenv
import logging

load_dotenv()

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Environment variables
GENIUS_ACCESS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Top artists data
top_artists = [
    {"name": "Adele", "image": "/static/images/Adele.jpeg"},
    {"name": "Drake", "image": "/static/images/Drake.jpeg"},
    {"name": "Taylor Swift", "image": "/static/images/TaylorSwift.jpeg"},
    {"name": "Burna Boy", "image": "/static/images/BurnaBoy.jpeg"},
    {"name": "Beyoncé", "image": "/static/images/Beyonce.jpeg"},
]

# ------------------ GENIUS ------------------
def get_lyrics_from_genius(artist, title):
    logger.debug(f"Fetching lyrics for artist: {artist}, title: {title}")
    base_url = "https://api.genius.com"
    headers = {'Authorization': f'Bearer {GENIUS_ACCESS_TOKEN}'}
    search_url = f"{base_url}/search"
    params = {'q': f'{artist} {title}'}

    # Genius API request
    response = requests.get(search_url, params=params, headers=headers)
    logger.debug(f"Genius API Response: {response.status_code} - {response.text}")

    if response.status_code != 200:
        logger.error(f"Error accessing Genius API: {response.status_code}")
        return None, "Error accessing Genius API."

    hits = response.json().get("response", {}).get("hits", [])
    if not hits:
        logger.info(f"No results found on Genius for artist: {artist}, title: {title}")
        return None, "Song not found on Genius."

    #fetch lyrics
    song_url = hits[0]["result"]["url"]
    logger.debug(f"Song URL: {song_url}")

    page = requests.get(song_url)
    html = BeautifulSoup(page.text, "html.parser")

    containers = html.find_all("div", {"data-lyrics-container": "true"})
    lyrics = "\n".join([c.get_text(separator="\n") for c in containers]) if containers else None

    if lyrics:
        logger.debug("Lyrics successfully retrieved.")
    else:
        logger.warning("Lyrics not found on Genius.")

    return lyrics.strip() if lyrics else None, "Lyrics not found on Genius."


# ------------------ MAIN ROUTE ------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    logger.info("Index route accessed.")
    lyrics = None
    error = None
    spotify_data = None

    if request.method == 'POST':
        artist = request.form.get('artist')
        title = request.form.get('title')
        logger.debug(f"Form submission received: artist={artist}, title={title}")

        lyrics, error = get_lyrics_from_genius(artist, title)
        if not lyrics:
            error = error or "Lyrics not found."
            logger.warning(f"Lyrics not found for artist={artist}, title={title}")

    return render_template(
        'index.html',
        lyrics=lyrics,
        error=error,
        top_artists=top_artists,
        spotify_data=spotify_data
    )

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port)