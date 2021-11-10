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
        Popularity = 100
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
        if track_id is None:
            return
        try:
            stmt = sqlalchemy.text("SELECT * FROM Track WHERE TrackId = TrackId")
            with self.db.connect() as conn:
                conn.execute(stmt, TrackId=track_id)
        except Exception as e:
            print("get_track_by_id")

    def get_track_with_features_by_id(self, track_id):
        pass

    def get_tracks_by_name(self, track_name):
        if track_name is None:
            return
        try:
            stmt = sqlalchemy.text("SELECT * FROM Track WHERE TrackName = TrackName")
            with self.db.connect() as conn:
                conn.execute(stmt, TrackName=track_name)
        except Exception as e:
            print("get_tracks_by_name")

    def get_tracks_with_features_by_name(self, track_name):
        pass

    def get_artist_by_name(self, artist_name: str) -> Dict[str, Any]:
        if artist_name is None:
            return None
        try:
            stmt = sqlalchemy.text("SELECT * FROM Artist WHERE LOWER(ArtistName) LIKE '%" + str(artist_name).lower() + "%' ORDER BY Popularity DESC")
            with self.db.connect() as conn:
                output = conn.execute(stmt)
            result = {}

            # Build resulting dict with attributes of artist
            columns = ['ArtistId', 'ArtistName', 'ImageUrl', 'Genre', 'Popularity']
            top_result = list(output)[0]
            for i, column in enumerate(columns):
                result[column] = top_result[i]
            return result
        except Exception as e:
            print(e)
        return None

    def get_albums_by_attributes(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        # attributes will have artist required, optional yearfrom, yearto, optional popularity rating, optional duration
        if attributes is None:
            return
        try:
            # Build query based on given attributes durationFrom durationTO
            query = "SELECT DISTINCT AlbumName FROM Album JOIN Artist ON Album.ArtistId = Artist.ArtistId WHERE LOWER(AlbumName) LIKE '%" +str(attributes['albumName']).lower() + "%' AND LOWER(ArtistName) LIKE '%" + str(attributes['artist']).lower() + "%' AND YEAR(ReleaseDate) BETWEEN " + str(attributes['yearFrom']) + " AND " + str(attributes['yearTo']) + " AND Album.Popularity >= " + str(attributes['popularityRating'])
            stmt = sqlalchemy.text(query)
            print(str(stmt))
            with self.db.connect() as conn:
                output = conn.execute(stmt)

            # Build dict result with attributes of album
            result = []
            columns = ["AlbumName"]
            for row in output:
                albumDict = {}
                for i, column in enumerate(columns):
                    albumDict[column] = row[i]
                result.append(albumDict)
            return result
        except Exception as e:
            print(e)

    def get_tracks_by_attributes(self, attributes: Dict[str, Any]) -> Dict[str, Any]:

        if attributes is None:
            return
        try:
            # Build query based on given attributes durationFrom durationTO
            query = "SELECT * FROM Track WHERE LOWER(TrackName) LIKE '%" + str(attributes['track']).lower() + "%' AND ArtistName LIKE '%" + str(attributes['artist']) + "%' AND Duration BETWEEN" + str(attributes['durationLowerBound']) + " AND " + str('attributes[durationUpperBound]') + " AND Popularity >= " + str(attributes['popularityRating'])
            stmt = sqlalchemy.text(query)
            with self.db.connect() as conn:
                output = conn.execute(stmt)

            # Build dict result with attributes of album
            result = []
            for row in output:
                trackDict = {}
                for key in row.keys():
                    trackDict[key] = row[key]
                result.append(trackDict)
            return result
        except Exception as e:
            print("get_tracks_by_attributes")

    def delete_track_by_id(self, track_id):
        pass

    def delete_album_by_id(self, album_id):
        pass

    def delete_artist_by_id(self, artist_id: str) -> bool:
        if artist_id is None:
            return
        try:
            stmt = sqlalchemy.text("DELETE From Artist WHERE ArtistId = :IdToDelete")
            with self.db.connect() as conn:
                result = conn.execute(stmt, IdToDelete=artist_id)
                if result.rowcount > 0:
                    return True
        except Exception as e:
            print("delete_artist_by_id")
        return False
    def get_tracks_by_popularity_and_artist_popularity(self, artistPopularityRating, trackPopularityRating):
        if artistPopularityRating is None or trackPopularityRating is None:
            return
        try:
            stmt = sqlalchemy.text("SELECT * FROM Tracks t WHERE EXISTS (SELECT * FROM Artist a JOIN TrackArtist ta ON a.ArtistId = ta.ArtistId WHERE t.TrackId = ta.TrackId AND t.Popularity > :trackPopularityToAdd AND a.Popularity > :artistPopularityToAdd) ORDER BY t.TrackName DESC LIMIT 10")
            with self.db.connect() as conn:
                output = conn.execute(stmt, trackPopularityToAdd=trackPopularityRating, artistPopularityToAdd=artistPopularityRating)
                # Build dict result with attributes of album
            result = []
            columns = ["TrackName", "ArtistName"]
            for row in output:
                albumDict = {}
                for i, column in enumerate(columns):
                    albumDict[column] = row[i]
                result.append(albumDict)
            return result
        except Exception as e:
            print(e, "get_tracks_by_popularity_and_artist_popularity")
        return False
    
    def get_albums_by_average_tempo(self, tempo):
        if tempo is None:
            return
        try:
            stmt = sqlalchemy.text("SELECT al.AlbumName, ROUND(AVG(tp.Tempo)) AS avgTrackPopularity FROM Album al JOIN Track t ON al.AlbumId = t.AlbumId JOIN TrackProperties tp ON t.TrackId = tp.TrackId GROUP BY al.AlbumName HAVING avgTrackPopularity > :tempoToAdd ORDER BY avgTrackPopularity DESC LIMIT 10")
            with self.db.connect() as conn:
                output = conn.execute(stmt, tempoToAdd=tempo)
                # Build dict result with attributes of album
            result = []
            columns = ["AlbumName"]
            for row in output:
                albumDict = {}
                for i, column in enumerate(columns):
                    albumDict[column] = row[i]
                result.append(albumDict)
            return result
        except Exception as e:
            print(e, "get_albums_by_average_tempo")
        return False
    
    def update_user_like(self, like_val, user_val, artist_id_val):
        try:
            stmt = sqlalchemy.text("UPDATE ArtistLikes SET Likes = :LikeVal WHERE Username = :UserVal AND ArtistId = :ArtistIdVal")
            with self.db.connect() as conn:
                result = conn.execute(stmt, LikeVal=like_val, UserVal=user_val, ArtistIdVal=artist_id_val)
                if result.rowcount > 0:
                    return True
        except Exception as e:
            print(e)
        return False
