DECLARE vtrackName VARCHAR(255);
DECLARE finished int default 0;
DECLARE trackCur CURSOR FOR (SELECT TrackName FROM LikedTracks);
DECLARE CONTINUE HANDLER FOR NOT FOUND SET finished = 1;

DROP TABLE IF EXISTS NewTable;  
CREATE TABLE NewTable(
TrackName VARCHAR(255) PRIMARY KEY);

OPEN trackCur;
REPEAT
    FETCH trackCur INTO vtrackName;
    INSERT IGNORE INTO NewTable VALUES(TrackName);
    UNTIL finished
END REPEAT;
CLOSE trackCur;