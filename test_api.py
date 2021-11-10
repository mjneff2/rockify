from typing import Any, List, Dict
import spotipy
from spotipy.client import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import config_data
import logging
from database import Database

logger = logging.getLogger(__name__)

class APIWrapper:
    def __init__(self, db: Database):
        self.spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=config_data.client_id, client_secret=config_data.client_secret))
        self.db = db

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
        results = self.spotify.artist_albums(artist['id'], limit=10)
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
                album['artist_id'] = artist['id']
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

    def fill_for_artist_by_search(self, artist):
        query = artist.replace(" ", "+")
        result = self.spotify.search(q=query, type='artist', limit=1)
        print(result)
        full_artists = self.get_full_artists_from_artists(result['artists']['items'])
        logger.error(f"Artists: {len(full_artists)}")
        print(full_artists)
        for artist in full_artists:
            self.db.insert_artist(artist)
            albums = self.get_top_albums_from_artist(artist)
            logger.error(f"Albums: {len(albums)}")
            for album in albums:
                album['artist_id'] = artist['id']
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

    def delete_artist_by_name(self, artist_name):
        artist = self.db.get_artist_by_name(artist_name)
        if artist is None:
            return False
        logger.error(artist)
        return self.db.delete_artist_by_id(artist['ArtistId'])

    def get_albums_by_attributes(self, data):
        return self.db.get_albums_by_data(data)