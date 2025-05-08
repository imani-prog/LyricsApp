from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import base64
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

GENIUS_ACCESS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

top_artists = [
    {"name": "Adele", "image": "/static/images/Adele.jpeg"},
    {"name": "Drake", "image": "/static/images/Drake.jpeg"},
    {"name": "Taylor Swift", "image": "/static/images/TaylorSwift.jpeg"},
    {"name": "Burna Boy", "image": "/static/images/BurnaBoy.jpeg"},
    {"name": "Beyoncé", "image": "/static/images/Beyonce.jpeg"},
]

# ------------------ GENIUS ------------------

def get_lyrics_from_genius(artist, title):
    base_url = "https://api.genius.com"
    headers = {'Authorization': f'Bearer {GENIUS_ACCESS_TOKEN}'}
    search_url = f"{base_url}/search"
    params = {'q': f'{artist} {title}'}
    response = requests.get(search_url, params=params, headers=headers)

    if response.status_code != 200:
        return None, "Error accessing Genius API."

    hits = response.json().get("response", {}).get("hits", [])
    if not hits:
        return None, "Song not found on Genius."

    song_url = hits[0]["result"]["url"]
    page = requests.get(song_url)
    html = BeautifulSoup(page.text, "html.parser")

    containers = html.select("div[class^='Lyrics__Container']")
    lyrics = "\n".join([c.get_text(separator="\n") for c in containers]) if containers else None

    return lyrics.strip() if lyrics else None, "Lyrics not found on Genius."


# ------------------ MAIN ROUTE ------------------

@app.route('/', methods=['GET', 'POST'])
def index():
    lyrics = None
    error = None
    spotify_data = None

    if request.method == 'POST':
        artist = request.form.get('artist')
        title = request.form.get('title')

        lyrics, error = get_lyrics_from_genius(artist, title)
        if not lyrics:
            error = error or "Lyrics not found."

    return render_template(
        'index.html',
        lyrics=lyrics,
        error=error,
        top_artists=top_artists,
        spotify_data=spotify_data
    )

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

