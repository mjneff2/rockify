import sqlalchemy
class Database:
    def insert_track(self, track):
        TrackId = track['id']
        TrackName = track['name']
        ImageURL = track['album']['images'][0]['url']
        Genre = "rock"
        Popularity = track['popularity']
        PreviewURL = track['preview_url']
        ReleaseDate = track['album']['release_date']
        Duration = track['duration_ms']
        
        pass

    def insert_artist(self, artist):
        ArtistId = artist['id']
        ArtistName = artist['name']
        ImageURL = "blank"
        Genre = "rock"
        Popularity = 0
        
        pass

    def insert_album(self, album):
        AlbumId = album['id']
        AlbumName = album['name']
        ImageURL = album['images'][0]['url']
        Genre = "rock"
        Popularity = 0
        ReleaseDate = album['release_date']  
        
        pass

    def insert_track_properties(self, track_properties):
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
        
        pass
