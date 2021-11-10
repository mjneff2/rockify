CREATE TABLE Artist(
ArtistId VARCHAR(255), 
ArtistName VARCHAR(255), 
ImageUrl VARCHAR(255), 
Genre VARCHAR(255), 
Popularity INT,
PRIMARY KEY(ArtistId)
);

CREATE TABLE Album(
AlbumId VARCHAR(255), 
AlbumName VARCHAR(255), 
ImageUrl VARCHAR(255), 
Genre VARCHAR(255), 
Popularity INT, 
ReleaseDate DATE,
ArtistId VARCHAR(255),
PRIMARY KEY (AlbumId),
FOREIGN KEY (ArtistId) REFERENCES Artist(ArtistId) ON DELETE CASCADE
);

CREATE TABLE Track(
TrackId VARCHAR(255),
TrackName VARCHAR(255), 
ImageURL VARCHAR(255), 
Genre VARCHAR(255), 
Popularity INT, 
PreviewURL VARCHAR(255), 
ReleaseDate DATE, 
Duration INT,
AlbumId VARCHAR(255),
ArtistId VARCHAR(255),
PRIMARY KEY (TrackId),
FOREIGN KEY (AlbumId) REFERENCES Album(AlbumId) ON DELETE CASCADE,
FOREIGN KEY (ArtistId) REFERENCES Artist(ArtistId) ON DELETE CASCADE
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
FOREIGN KEY(TrackId) REFERENCES Track(TrackId) ON DELETE CASCADE
);

CREATE TABLE TrackArtist(
TrackId VARCHAR(255), 
ArtistId VARCHAR(255), 
IsFeature BOOLEAN,
PRIMARY KEY(TrackId, ArtistId),
FOREIGN KEY(TrackId) REFERENCES Track(TrackId) ON DELETE CASCADE,
FOREIGN KEY (ArtistId) REFERENCES Artist(ArtistId) ON DELETE CASCADE
);

CREATE TABLE User(
Username VARCHAR(255), 
PasswordHash VARCHAR(255), 
AuthToken VARCHAR(255),
PRIMARY KEY (Username)
);

CREATE TABLE ArtistLikes(
Username VARCHAR(255),
ArtistId VARCHAR(255),
Likes BOOLEAN,
PRIMARY KEY(Username, ArtistId),
FOREIGN KEY(Username) REFERENCES User(Username) ON DELETE CASCADE,
FOREIGN KEY(ArtistId) REFERENCES Artist(ArtistId) ON DELETE CASCADE
);