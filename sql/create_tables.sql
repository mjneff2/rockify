CREATE TABLE Track(
TrackId VARCHAR(255) [PK] [FK to TrackFeatures.TrackId, TrackArtist.TrackId],
TrackName VARCHAR(255), 
ImageURL VARCHAR(255), 
Genre VARCHAR(255), 
Popularity INT, 
PreviewURL VARCHAR(255), 
ReleaseDate DATE, 
Duration INT,
PRIMARY KEY(TrackId)
);


CREATE TABLE TrackProperties(
TrackId VARCHAR(255), 
Danceability REAL, 
Energy REAL, 
Loudness REAL, 
Speechiness REAL, 
Acousticness REAL, 
Instrumentalness REAL, 
Liveness REAL, 
Valence REAL, 
Tempo REAL,
PRIMARY KEY(TrackId)
);


CREATE TABLE TrackArtist(
TrackId VARCHAR(255) [PK], 
ArtistId VARCHAR(255) [FK to Artist.ArtistId], 
IsFeature BOOLEAN
PRIMARY KEY(TrackId, ArtistId)
);


CREATE TABLE Artist(
ArtistId VARCHAR(255) [PK], 
ArtistName, VARCHAR(255), 
ImageUrl, VARCHAR(255), 
Genre VARCHAR(255), 
Popularity INT
PRIMARY KEY(ArtistId)
);

CREATE TABLE User(
Username VARCHAR(255) PRIMARY KEY, 
PasswordHash VARCHAR(255), 
AuthToken VARCHAR(255)
);

CREATE TABLE Album(
AlbumId VARCHAR(255) PRIMARY KEY, 
AlbumName VARCHAR(255), 
ImageUrl VARCHAR(255), 
Genre VARCHAR(255), 
Popularity INT, 
ReleaseDate Character(Display Format: YYYY-MM-DDTHH:MM:SSZ)
);
