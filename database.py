import sqlalchemy
class Database:
    def __init__(self):
        self.track_calls = 0
        self.artist_calls = 0
        self.album_calls = 0
        self.track_feature_calls = 0

    def insert_track(self, track):
        if track is None:
            return
        TrackId = track['id']
        TrackName = track['name']
        mageURL = track['album']['images'][0]['url']
        Genre = "rock"
        Popularity = track['popularity']
        PreviewURL = track['preview_url']
        ReleaseDate = track['album']['release_date']
        Duration = track['duration_ms']
        self.track_calls += 1
        pass

    def insert_artist(self, artist):
        if artist is None:
            return
        ArtistId = artist['id']
        ArtistName = artist['name']
        ImageURL = "blank"
        Genre = "rock"
        Popularity = 0
        self.artist_calls += 1
        pass

    def insert_album(self, album):
        if album is None:
            return
        AlbumId = album['id']
        AlbumName = album['name']
        ImageURL = album['images'][0]['url']
        Genre = "rock"
        Popularity = 0
        ReleaseDate = album['release_date']  
        self.album_calls += 1
        pass

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
        pass
