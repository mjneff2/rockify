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