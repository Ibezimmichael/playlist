from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()
SPOTIFY_ID = os.environ.get('SPOTIFY_ID')
SPOTIFY_KEY = os.environ.get('SPOTIFY_KEY')

date = input("choose a date pick top rated songs: in this format YYYY-MM-DD\n")

url = f'https://www.billboard.com/charts/hot-100/{date}'
response = requests.get(url).text
soup = BeautifulSoup(response, "html.parser")
songs = [item.getText().strip() for item in soup.select(selector="main li h3")]
artist_scraped = [item.getText().strip() for item in soup.find_all(name="span", class_="c-label")]
artists = [artist.split(" Featuring")[0].split(" Duet")[0].replace("$", "s") for artist in artist_scraped
           if not artist.isnumeric()
           if artist != "-"
           if artist != "NEW"
           if 'ENTRY' not in artist
           ]
print(songs)
print(artists)
song_uris = []
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=SPOTIFY_ID,
        client_secret=SPOTIFY_KEY,
        redirect_uri="https://localhost:5501/callback/",
        cache_path="token.txt",
        scope="playlist-modify-private",
    ))
user_id = sp.current_user()["id"]
user_name = sp.current_user()["display_name"]
year = date.split("-")[0]
for song, artist in zip(songs, artists):
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    print(result)
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} is not available on spotify")

playlist = sp.user_playlist_create(user=user_id, name=f"{date} billboard top 100", public=False)

sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)
