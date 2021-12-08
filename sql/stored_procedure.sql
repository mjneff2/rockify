CREATE PROCEDURE MakeLikedTracks(
    IN type VARCHAR(10),
    IN identity VARCHAR(255)
)
BEGIN
DROP TABLE IF EXISTS LikedTracks;
CREATE TABLE LikedTracks(
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
Likes BOOLEAN,
PRIMARY KEY(TrackId)
);

IF type = "Track" THEN
    INSERT IGNORE INTO LikedTracks 
    (SELECT TrackId, Danceability, Energy, Loudness, Speechiness, Acousticness, Instrumentalness, Liveness, Valence, Tempo, Likes
    FROM TrackLikes tl NATURAL JOIN Track t NATURAL JOIN TrackProperties tp WHERE Username = identity);
END IF;
IF type = "Album" THEN
    INSERT IGNORE INTO LikedTracks 
    (SELECT TrackId, Danceability, Energy, Loudness, Speechiness, Acousticness, Instrumentalness, Liveness, Valence, Tempo, Likes
    FROM AlbumLikes al NATURAL JOIN Album a JOIN Track t ON a.AlbumId = t.AlbumId NATURAL JOIN TrackProperties tp WHERE Username = identity);
END IF;
IF type = "Artist" THEN
    INSERT IGNORE INTO LikedTracks 
    (SELECT TrackId, Danceability, Energy, Loudness, Speechiness, Acousticness, Instrumentalness, Liveness, Valence, Tempo, Likes 
    FROM ArtistLikes al NATURAL JOIN Artist a JOIN Album alb ON a.ArtistId = alb.ArtistId JOIN Track t ON alb.AlbumId = t.AlbumId NATURAL JOIN TrackProperties tp WHERE Username = identity);
END IF;

END;

CREATE PROCEDURE Recommend(
    IN type VARCHAR(10),
    IN identity VARCHAR(255))
BEGIN

DECLARE vTrackId VARCHAR(255);
DECLARE vDanceability REAL;
DECLARE vEnergy REAL;
DECLARE vLoudness REAL;
DECLARE vSpeechiness REAL;
DECLARE vAcousticness REAL;
DECLARE vInstrumentalness REAL;
DECLARE vLiveness REAL;
DECLARE vValence REAL;
DECLARE vTempo REAL;
DECLARE vLikes BOOLEAN;
DECLARE vCount INT default 0;
DECLARE finished int default 0;
DECLARE trackCur CURSOR FOR (SELECT * FROM LikedTracks);
DECLARE CONTINUE HANDLER FOR NOT FOUND SET finished = 1;

DROP TABLE IF EXISTS NewTable;  
CREATE TABLE NewTable(
Username VARCHAR(255),
Danceability REAL, 
Energy REAL, 
Loudness REAL, 
Speechiness REAL, 
Acousticness REAL, 
Instrumentalness REAL, 
Liveness REAL, 
Valence REAL, 
Tempo REAL);

INSERT INTO NewTable VALUES(identity, 0, 0, 0, 0, 0, 0, 0, 0, 0);

OPEN trackCur;
REPEAT
    FETCH trackCur INTO vTrackId, vDanceability, vEnergy, vLoudness, vSpeechiness, vAcousticness, vInstrumentalness, vLiveness, vValence, vTempo, vLikes;
    IF vLikes THEN
        UPDATE NewTable SET Danceability = Danceability + vDanceability, Energy = Energy + vEnergy, Loudness = Loudness + vLoudness, Speechiness = Speechiness + vSpeechiness, Acousticness = Acousticness + vAcousticness, Instrumentalness = Instrumentalness + vInstrumentalness, Liveness = Liveness + vLiveness, Valence = Valence + vValence, Tempo = Tempo + vTempo;
    ELSE
        UPDATE NewTable SET Danceability = Danceability - vDanceability, Energy = Energy - vEnergy, Loudness = Loudness - vLoudness, Speechiness = Speechiness - vSpeechiness, Acousticness = Acousticness - vAcousticness, Instrumentalness = Instrumentalness - vInstrumentalness, Liveness = Liveness - vLiveness, Valence = Valence - vValence, Tempo = Tempo - vTempo;
    END IF;
    SET vCount = vCount + 1;
    UNTIL finished
END REPEAT;
CLOSE trackCur;

SELECT Danceability / vCount INTO vDanceability FROM NewTable;
SELECT Energy / vCount INTO vEnergy FROM NewTable;
SELECT Loudness / vCount INTO vLoudness FROM NewTable;
SELECT Speechiness / vCount INTO vSpeechiness FROM NewTable;
SELECT Acousticness / vCount INTO vAcousticness FROM NewTable;
SELECT Instrumentalness / vCount INTO vInstrumentalness FROM NewTable;
SELECT Liveness / vCount INTO vLiveness FROM NewTable;
SELECT Valence / vCount INTO vValence FROM NewTable;
SELECT Tempo / vCount INTO vTempo FROM NewTable;

IF type = "Artist" THEN
    SELECT a.ArtistId, a.ArtistName, a.ImageURL, a.Genre, a.Popularity
    FROM Artist a JOIN Album al ON a.ArtistId = al.ArtistId JOIN Track t on al.AlbumId = t.AlbumId NATURAL JOIN TrackProperties
    GROUP BY a.ArtistId
    HAVING avg(Danceability) BETWEEN vDanceability - 0.2 AND vDanceability + 0.2 
        AND avg(Energy) BETWEEN vEnergy - 0.2 AND vEnergy + 0.2
        AND avg(Loudness) BETWEEN vLoudness - 20 AND vLoudness + 20
        AND avg(Speechiness) BETWEEN vSpeechiness - 0.2 AND vSpeechiness + 0.2
        AND avg(Acousticness) BETWEEN vAcousticness - 0.2 AND vAcousticness + 0.2
        AND avg(Instrumentalness) BETWEEN vInstrumentalness - 0.2 AND vInstrumentalness + 0.2
        AND avg(Liveness) BETWEEN vLiveness - 0.2 AND vLiveness + 0.2
        AND avg(Valence) BETWEEN vValence - 0.2 AND vValence + 0.2
        AND avg(Tempo) BETWEEN vTempo - 60 AND vTempo + 60;

ELSEIF type = "Album" THEN
    SELECT a.AlbumId, a.AlbumName, a.ImageURL, a.Genre, a.Popularity, a.ReleaseDate, a.ArtistId
    FROM Album a JOIN Track t on a.AlbumId = t.AlbumId NATURAL JOIN TrackProperties
    GROUP BY a.AlbumId
    HAVING avg(Danceability) BETWEEN vDanceability - 0.2 AND vDanceability + 0.2 
        AND avg(Energy) BETWEEN vEnergy - 0.2 AND vEnergy + 0.2
        AND avg(Loudness) BETWEEN vLoudness - 20 AND vLoudness + 20
        AND avg(Speechiness) BETWEEN vSpeechiness - 0.2 AND vSpeechiness + 0.2
        AND avg(Acousticness) BETWEEN vAcousticness - 0.2 AND vAcousticness + 0.2
        AND avg(Instrumentalness) BETWEEN vInstrumentalness - 0.2 AND vInstrumentalness + 0.2
        AND avg(Liveness) BETWEEN vLiveness - 0.2 AND vLiveness + 0.2
        AND avg(Valence) BETWEEN vValence - 0.2 AND vValence + 0.2
        AND avg(Tempo) BETWEEN vTempo - 60 AND vTempo + 60;

ELSEIF type = "Track" THEN
    SELECT TrackId, TrackName, ImageURL, Genre, Popularity, PreviewURL, ReleaseDate 
    FROM Track NATURAL JOIN TrackProperties
    WHERE Danceability BETWEEN vDanceability - 0.2 AND vDanceability + 0.2 
        AND Energy BETWEEN vEnergy - 0.2 AND vEnergy + 0.2
        AND Loudness BETWEEN vLoudness - 20 AND vLoudness + 20
        AND Speechiness BETWEEN vSpeechiness - 0.2 AND vSpeechiness + 0.2
        AND Acousticness BETWEEN vAcousticness - 0.2 AND vAcousticness + 0.2
        AND Instrumentalness BETWEEN vInstrumentalness - 0.2 AND vInstrumentalness + 0.2
        AND Liveness BETWEEN vLiveness - 0.2 AND vLiveness + 0.2
        AND Valence BETWEEN vValence - 0.2 AND vValence + 0.2
        AND Tempo BETWEEN vTempo - 60 AND vTempo + 60
        AND TrackId NOT IN (SELECT TrackId FROM TrackLikes WHERE Username = identity);
END IF;

END;