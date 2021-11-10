import sqlalchemy
from typing import Any, Dict

class Database:
    def __init__(self, db):
        self.track_calls = 0
        self.artist_calls = 0
        self.album_calls = 0
        self.track_feature_calls = 0
        self.db = db

    def insert_track(self, track):
        if track is None:
            return
        TrackId = track['id']
        TrackName = track['name']
        ImageURL = track['album']['images'][0]['url']
        Genre = "rock"
        Popularity = track['popularity']
        PreviewURL = track['preview_url']
        ReleaseDate = track['album']['release_date']
        Duration = track['duration_ms']
        AlbumId = track['album']['id']
        self.track_calls += 1
        try:
            stmt = sqlalchemy.text("INSERT INTO Track (TrackId, TrackName, ImageURL, Genre, Popularity, PreviewURL, ReleaseDate, Duration, AlbumId)" " VALUES (:TrackId, :TrackName, :ImageURL, :Genre, :Popularity, :PreviewURL, :ReleaseDate, :Duration, :AlbumId)")
            with self.db.connect() as conn:
                conn.execute(stmt, TrackId=TrackId, TrackName=TrackName, ImageURL=ImageURL,
                             Genre=Genre, Popularity=Popularity, PreviewURL=PreviewURL,
                             ReleaseDate=ReleaseDate, Duration=Duration, AlbumId=AlbumId)
            for artist in track['artists']:
                ArtistId = artist['id']
                stmt2 = sqlalchemy.text("INSERT INTO TrackArtist (TrackId, ArtistId)" " VALUES (:TrackId, :ArtistId)")
                with self.db.connect() as conn:
                    conn.execute(stmt2, TrackId=TrackId, ArtistId=ArtistId)  
        except Exception as e:
            print(e)

    def insert_artist(self, artist):
        if artist is None:
            return
        ArtistId = artist['id']
        ArtistName = artist['name']
        ImageURL = "blank"
        Genre = "rock"
        Popularity = 0
        self.artist_calls += 1
        try:
            stmt = sqlalchemy.text("INSERT INTO Artist (ArtistId, ArtistName, ImageURL, Genre, Popularity)" " VALUES (:ArtistId, :ArtistName, :ImageURL, :Genre, :Popularity)")
            with self.db.connect() as conn:
                conn.execute(stmt, ArtistId=ArtistId, ArtistName=ArtistName, ImageURL=ImageURL,
                             Genre=Genre, Popularity=Popularity)
        except Exception as e:
            print(e)

    def insert_album(self, album):
        if album is None:
            return
        AlbumId = album['id']
        AlbumName = album['name']
        ImageURL = album['images'][0]['url']
        Genre = "rock"
        Popularity = 0
        ReleaseDate = album['release_date']  
        ArtistId = album['artist_id']
        self.album_calls += 1
        try:
            stmt = sqlalchemy.text("INSERT INTO Album (AlbumId, AlbumName, ImageURL, Genre, Popularity, ReleaseDate, ArtistId)" " VALUES (:AlbumId, :AlbumName, :ImageURL, :Genre, :Popularity, :ReleaseDate, :ArtistId)")
            with self.db.connect() as conn:
                conn.execute(stmt, AlbumId=AlbumId, AlbumName=AlbumName, ImageURL=ImageURL,
                             Genre=Genre, Popularity=Popularity, ReleaseDate=ReleaseDate, ArtistId=ArtistId)
        except Exception as e:
            print(e)

    def insert_track_properties(self, track_properties):
        if track_properties is None:
            return
        TrackId = track_properties['id']
        Danceability = track_properties['danceability']
        Energy = track_properties['energy']
        Loudness = track_properties['loudness']
        Speechiness = track_properties['speechiness']
        Acousticness = track_properties['acousticness']
        Instrumentalness = track_properties['instrumentalness']
        Liveness = track_properties['liveness']
        Valence = track_properties['valence']
        Tempo = track_properties['tempo']
        self.track_feature_calls += 1
        try:
            stmt = sqlalchemy.text("INSERT INTO TrackProperties (TrackId, Danceability, Energy, Loudness, Speechiness, Acousticness, Instrumentalness, Liveness, Valence, Tempo)" " VALUES (:TrackId, :Danceability, :Energy, :Loudness, :Speechiness, :Acousticness, :Instrumentalness, :Liveness, :Valence, :Tempo)")
            with self.db.connect() as conn:
                conn.execute(stmt, TrackId=TrackId, Danceability=Danceability,
                             Energy=Energy, Loudness=Loudness, Speechiness=Speechiness,
                             Acousticness=Acousticness, Instrumentalness=Instrumentalness,
                             Liveness=Liveness, Valence=Valence, Tempo=Tempo)
        except Exception as e:
            print(e)

    def get_track_by_id(self, track_id):
        pass

    def get_track_with_features_by_id(self, track_id):
        pass

    def get_tracks_by_name(self, track_name):
        pass

    def get_tracks_with_features_by_name(self, track_name):
        pass

    def get_artist_by_name(self, artist_name: str) -> Dict[str, Any]:
        pass

    def get_albums_by_attributes(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        # attributes will have artist required, optional yearfrom, yearto, optional popularity rating, optional duration
        pass

    def delete_track_by_id(self, track_id):
        pass

    def delete_album_by_id(self, album_id):
        pass

    def delete_artist_by_id(self, artist_id: str) -> bool:
        pass
    

