CREATE TABLE Track(
TrackId VARCHAR(255) [PK] [FK to TrackFeatures.TrackId, TrackArtist.TrackId],
TrackName VARCHAR(255), 
ImageURL VARCHAR(255), 
Genre VARCHAR(255), 
Popularity INT, 
PreviewURL VARCHAR(255), 
ReleaseDate DATE, 
Duration INT,
AlbumId VARCHAR(255),
PRIMARY KEY (TrackId),
FOREIGN KEY (AlbumId) REFERENCES Album(AlbumId)
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
PRIMARY KEY(TrackId),
FOREIGN KEY(TrackId) REFERENCES Track(TrackId)
);


CREATE TABLE TrackArtist(
TrackId VARCHAR(255), 
ArtistId VARCHAR(255) [FK to Artist.ArtistId], 
IsFeature BOOLEAN,
PRIMARY KEY(TrackId, ArtistId),
FOREIGN KEY(TrackId) REFERENCES Track(TrackId),
FOREIGN KEY (ArtistId) REFERENCES Artist(ArtistId)
);


CREATE TABLE Artist(
ArtistId VARCHAR(255), 
ArtistName VARCHAR(255), 
ImageUrl VARCHAR(255), 
Genre VARCHAR(255), 
Popularity INT,
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
ReleaseDate DATE
);
