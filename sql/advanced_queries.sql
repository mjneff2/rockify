SELECT YEAR(al.ReleaseDate) AS YearReleased, COUNT(al.AlbumName)
FROM Artist ar JOIN Album al ON ar.ArtistId = al.ArtistId
WHERE YEAR(al.ReleaseDate) < 1980 AND ar.ArtistName = "The Rolling Stones"
GROUP BY YEAR(al.ReleaseDate)
ORDER BY YEAR(al.ReleaseDate), COUNT(al.AlbumName) DESC;

(SELECT DISTINCT t.TrackName, a.ArtistName, t.Popularity, t.Duration
FROM Artist a JOIN TrackArtist ta ON a.ArtistId = ta.ArtistId JOIN Track t ON t.TrackId = ta.TrackId
WHERE a.ArtistName = "AC/DC" AND t.Popularity < 50 AND t.Duration > 120000)
UNION
(SELECT DISTINCT t.TrackName, a.ArtistName, t.Popularity, t.Duration
FROM Artist a JOIN TrackArtist ta ON a.ArtistId = ta.ArtistId JOIN Track t ON t.TrackId = ta.TrackId
WHERE a.ArtistName = "Nirvana" AND t.Popularity < 50 AND t.Duration > 120000)
LIMIT 15;

--New Advanced Queries
--Get tracks with popularity > 50 from Artists with popularity > 70
SELECT *
FROM Tracks t
WHERE EXISTS (SELECT * FROM Artists a JOIN TrackArtist ta ON a.ArtistId = ta.ArtistId
							WHERE t.TrackId = ta.TrackId AND t.Popularity > 50 AND a.Popularity > 70)
ORDER BY t.TrackName DESC;

--Get albums where average have tempo > 90
SELECT al.AlbumName, ROUND(AVG(tp.Tempo)) AS avgTrackPopularity
FROM Albums al JOIN Tracks t ON al.AlbumId = t.AlbumId JOIN TrackProperties tp ON t.TrackId = tp.TrackId
GROUP BY al.albumNameToGet
HAVING avgTrackPopularity > 90
ORDER BY avgTrackPopularity DESC;
