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
            results = self.spotify.next(results)['playlists']
            if results['items']:
                playlists.extend(results['items'])
        return playlists
            
    def get_artists_from_playlist(self, playlist):
        results = self.spotify.playlist_tracks(playlist['id'])
        tracks = results['items']
        while results['next']:
            results = self.spotify.next(results)
            if results['items']:
                tracks.extend(results['items'])
        simple_artists = []
        for track in tracks:
            if track:
                track = track['track']
                if track:
                    artists = track['artists']
                    if artists:
                        for artist in artists:
                            if artist:
                                simple_artists.append(artist)
        return simple_artists

    def get_full_artists_from_artists(self, artists):
        ids = [artist['id'] for artist in artists]
        ids = self.remove_duplicates(ids)
        full_artists = []
        for i in range(0, len(ids), 50):
            results = self.spotify.artists(ids[i:i+50])
            if results['artists']:
                full_artists.extend(results['artists'])
        return full_artists

    def remove_duplicates(self, input):
        return list(set(input))

    def get_top_albums_from_artist(self, artist):
        results = self.spotify.artist_albums(artist['id'])
        albums = results['items']
        return albums
            
    def get_tracks_from_album(self, album):
        results = self.spotify.album_tracks(album['id'])
        tracks = results['items']
        while results['next']:
            results = self.spotify.next(results)
            if results['items']:
                tracks.extend(results['items'])
        return tracks

    def get_full_tracks_from_tracks(self, tracks):
        ids = [track['id'] for track in tracks]
        full_tracks = []
        for i in range(0, len(ids), 50):
            results = self.spotify.tracks(ids[i:i+50])
            if results['tracks']:
                full_tracks.extend(results['tracks'])
        return full_tracks

    def get_track_features_from_tracks(self, tracks):
        ids = [track['id'] for track in tracks]
        features_list = []
        for i in range(0, len(ids), 50):
            results = self.spotify.audio_features(ids[i:i+50])
            if results:
                features_list.extend(results)
        return features_list

    def fill_database(self):
        playlists = self.get_playlists_from_rock()
        logger.error(f"Playlists: {len(playlists)}")
        simple_artists = []
        for playlist in playlists:
            simple_artists.extend(self.get_artists_from_playlist(playlist))
        full_artists = self.get_full_artists_from_artists(simple_artists)
        logger.error(f"Artists: {len(full_artists)}")
        for artist in full_artists:
            self.db.insert_artist(artist)
            albums = self.get_top_albums_from_artist(artist)
            logger.error(f"Albums: {len(albums)}")
            for album in albums:
                self.db.insert_album(album)
                simple_tracks = self.get_tracks_from_album(album)
                full_tracks = self.get_full_tracks_from_tracks(simple_tracks)
                logger.error(f"Tracks: {len(full_tracks)}")
                for track in full_tracks:
                    self.db.insert_track(track)
                track_features_list = self.get_track_features_from_tracks(full_tracks)
                for track_features in track_features_list:
                    self.db.insert_track_properties(track_features)
        logger.error(f"{self.db.track_feature_calls}, {self.db.track_calls}, {self.db.artist_calls}, {self.db.album_calls}")
        

if __name__ == "__main__":
    api = APIWrapper()
    api.fill_database()