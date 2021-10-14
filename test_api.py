from typing import Any, List, Dict
import spotipy
from spotipy.client import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import config
import logging

logger = logging.getLogger(__name__)

class APIWrapper:
    def __init__(self):
        self.spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=config.client_id, client_secret=config.client_secret))

    def get_playlists_from_rock(self):
        track_count = 0
        results = self.spotify.category_playlists(category_id="rock", limit=50)['playlists']
        playlists = results['items']
        while results['next']:
            results = self.spotify.next(results)
            playlists.extend(results['items'])
        for playlist in playlists:
            track_count += self.get_songs_from_playlist(playlist)
        print(track_count)
        print(len(playlists))
            
    def get_songs_from_playlist(self, playlist):
        results = self.spotify.playlist_tracks(playlist['id'])
        #print(results)
        tracks = results['items']
        while results['next']:
            results = self.spotify.next(results)
            tracks.extend(results['items'])
        for track in tracks:
            print(track['track']['name'], end="")
            for artist in track['track']['artists']:
                print(" - ", artist['name'], end="")
            print()
        return len(tracks)
        

if __name__ == "__main__":
    api = APIWrapper()
    api.get_playlists_from_rock()