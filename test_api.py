from typing import Any, List, Dict
import spotipy
from spotipy.client import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import config
import logging
import database

logger = logging.getLogger(__name__)

class APIWrapper:
    def __init__(self):
        self.spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=config.client_id, client_secret=config.client_secret))
        self.db = database.Database()

    def get_playlists_from_rock(self):
        results = self.spotify.category_playlists(category_id="rock", limit=50)['playlists']
        playlists = results['items']
        while results['next']:
            results = self.spotify.next(results)
            playlists.extend(results['items'])
        for playlist in playlists:
            self.get_artists_from_playlist(playlist)
            
    def get_artists_from_playlist(self, playlist):
        results = self.spotify.playlist_tracks(playlist['id'])
        tracks = results['items']
        while results['next']:
            results = self.spotify.next(results)
            tracks.extend(results['items'])
        artists = []
        for track in tracks:
            self.db.insert_track(track['track'])
            for artist in track['track']['artists']:
                artists.append(artist)
                self.db.insert_artist(artist)

    def get_top_albums_from_artist(self, artist):
        results = self.spotify.artist_albums(artist['id'])
        albums = results['items']
        while results['next']:
            results = self.spotify.next(results)
            albums.extend(results['items'])
        for album in albums:
            self.db.insert_album(album)
            self.get_tracks_from_album(album)
            
    def get_tracks_from_album(self, album):
        results = self.spotify.album_tracks(album['id'])
        tracks = results['items']
        while results['next']:
            results = self.spotify.next(results)
            tracks.extend(results['items'])
        for track in tracks:
            self.db.insert_track(track)
            self.get_track_features_from_track(track)

    def get_track_features_from_track(self, track):
        pass
        

if __name__ == "__main__":
    api = APIWrapper()
    api.get_playlists_from_rock()