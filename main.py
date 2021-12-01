# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from flask import Flask, request, jsonify
from flask_cors import CORS
from markupsafe import escape
import sqlalchemy
import flask_praetorian
from sqlalchemy.exc import IntegrityError

from database import Database
from test_api import APIWrapper

class User:
    def __init__(self):
        self.identity = None
        self.password = None
        self.rolenames = None

    @classmethod
    def lookup(cls, username):
        """
        *Required Method*
        flask-praetorian requires that the user class implements a ``lookup()``
        class method that takes a single ``username`` argument and returns a user
        instance if there is one that matches or ``None`` if there is not.
        """
        with db.connect() as conn:
            result = conn.execute(
                "SELECT Username, PasswordHash From User WHERE Username = '" + username + "'"
            ).first()
            if not result:
                return None
            user = User()
            user.identity = result[0]
            user.password = result[1]
            user.rolenames = "User"
            return user


    @classmethod
    def identify(cls, id):
        """
        *Required Method*
        flask-praetorian requires that the user class implements an ``identify()``
        class method that takes a single ``id`` argument and returns user instance if
        there is one that matches or ``None`` if there is not.
        """
        return cls.lookup(id)

    def is_valid(self):
        return True

db = None
guard = flask_praetorian.Praetorian()
cors = CORS()
api = None
app = Flask(__name__)
app.config["SECRET_KEY"] = "top secret"
app.config["JWT_ACCESS_LIFESPAN"] = {"hours": 24}
app.config["JWT_REFRESH_LIFESPAN"] = {"days": 30}
guard.init_app(app, User)
cors.init_app(app)

def init_connection_engine():
    db_config = {
        # [START cloud_sql_mysql_sqlalchemy_limit]
        # Pool size is the maximum number of permanent connections to keep.
        "pool_size": 5,
        # Temporarily exceeds the set pool_size if no connections are available.
        "max_overflow": 2,
        # The total number of concurrent connections for your application will be
        # a total of pool_size and max_overflow.
        # [END cloud_sql_mysql_sqlalchemy_limit]

        # [START cloud_sql_mysql_sqlalchemy_backoff]
        # SQLAlchemy automatically uses delays between failed connection attempts,
        # but provides no arguments for configuration.
        # [END cloud_sql_mysql_sqlalchemy_backoff]

        # [START cloud_sql_mysql_sqlalchemy_timeout]
        # 'pool_timeout' is the maximum number of seconds to wait when retrieving a
        # new connection from the pool. After the specified amount of time, an
        # exception will be thrown.
        "pool_timeout": 30,  # 30 seconds
        # [END cloud_sql_mysql_sqlalchemy_timeout]

        # [START cloud_sql_mysql_sqlalchemy_lifetime]
        # 'pool_recycle' is the maximum number of seconds a connection can persist.
        # Connections that live longer than the specified amount of time will be
        # reestablished
        "pool_recycle": 1800,  # 30 minutes
        # [END cloud_sql_mysql_sqlalchemy_lifetime]

    }

    if os.environ.get("DB_HOST"):
        if os.environ.get("DB_ROOT_CERT"):
            return init_tcp_sslcerts_connection_engine(db_config)
        return init_tcp_connection_engine(db_config)
    return init_unix_connection_engine(db_config)


def init_tcp_sslcerts_connection_engine(db_config):
    # [START cloud_sql_mysql_sqlalchemy_create_tcp_sslcerts]
    # Remember - storing secrets in plaintext is potentially unsafe. Consider using
    # something like https://cloud.google.com/secret-manager/docs/overview to help keep
    # secrets secret.
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASS"]
    db_name = os.environ["DB_NAME"]
    db_host = os.environ["DB_HOST"]
    db_root_cert = os.environ["DB_ROOT_CERT"]
    db_cert = os.environ["DB_CERT"]
    db_key = os.environ["DB_KEY"]

    # Extract port from db_host if present,
    # otherwise use DB_PORT environment variable.
    host_args = db_host.split(":")
    if len(host_args) == 1:
        db_hostname = host_args[0]
        db_port = int(os.environ["DB_PORT"])
    elif len(host_args) == 2:
        db_hostname, db_port = host_args[0], int(host_args[1])

    ssl_args = {
        "ssl_ca": db_root_cert,
        "ssl_cert": db_cert,
        "ssl_key": db_key
    }

    pool = sqlalchemy.create_engine(
        # Equivalent URL:
        # mysql+pymysql://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>
        sqlalchemy.engine.url.URL.create(
            drivername="mysql+pymysql",
            username=db_user,  # e.g. "my-database-user"
            password=db_pass,  # e.g. "my-database-password"
            host=db_hostname,  # e.g. "127.0.0.1"
            port=db_port,  # e.g. 3306
            database=db_name  # e.g. "my-database-name"
        ),
        connect_args=ssl_args,
        **db_config
    )
    # [END cloud_sql_mysql_sqlalchemy_create_tcp_sslcerts]

    return pool


def init_tcp_connection_engine(db_config):
    # [START cloud_sql_mysql_sqlalchemy_create_tcp]
    # Remember - storing secrets in plaintext is potentially unsafe. Consider using
    # something like https://cloud.google.com/secret-manager/docs/overview to help keep
    # secrets secret.
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASS"]
    db_name = os.environ["DB_NAME"]
    db_host = os.environ["DB_HOST"]

    # Extract port from db_host if present,
    # otherwise use DB_PORT environment variable.
    host_args = db_host.split(":")
    if len(host_args) == 1:
        db_hostname = db_host
        db_port = os.environ["DB_PORT"]
    elif len(host_args) == 2:
        db_hostname, db_port = host_args[0], int(host_args[1])

    pool = sqlalchemy.create_engine(
        # Equivalent URL:
        # mysql+pymysql://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>
        sqlalchemy.engine.url.URL.create(
            drivername="mysql+pymysql",
            username=db_user,  # e.g. "my-database-user"
            password=db_pass,  # e.g. "my-database-password"
            host=db_hostname,  # e.g. "127.0.0.1"
            port=db_port,  # e.g. 3306
            database=db_name,  # e.g. "my-database-name"
        ),
        **db_config
    )
    # [END cloud_sql_mysql_sqlalchemy_create_tcp]

    return pool


def init_unix_connection_engine(db_config):
    # [START cloud_sql_mysql_sqlalchemy_create_socket]
    # Remember - storing secrets in plaintext is potentially unsafe. Consider using
    # something like https://cloud.google.com/secret-manager/docs/overview to help keep
    # secrets secret.
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASS"]
    db_name = os.environ["DB_NAME"]
    db_socket_dir = os.environ.get("DB_SOCKET_DIR", "/cloudsql")
    cloud_sql_connection_name = os.environ["CLOUD_SQL_CONNECTION_NAME"]

    pool = sqlalchemy.create_engine(
        # Equivalent URL:
        # mysql+pymysql://<db_user>:<db_pass>@/<db_name>?unix_socket=<socket_path>/<cloud_sql_instance_name>
        sqlalchemy.engine.url.URL.create(
            drivername="mysql+pymysql",
            username=db_user,  # e.g. "my-database-user"
            password=db_pass,  # e.g. "my-database-password"
            database=db_name,  # e.g. "my-database-name"
            query={
                "unix_socket": "{}/{}".format(
                    db_socket_dir,  # e.g. "/cloudsql"
                    cloud_sql_connection_name)  # i.e "<PROJECT-NAME>:<INSTANCE-REGION>:<INSTANCE-NAME>"
            }
        ),
        **db_config
    )
    # [END cloud_sql_mysql_sqlalchemy_create_socket]

    return pool

@app.before_first_request
def init_database_and_api():
    global db
    global api
    db = db or init_connection_engine()
    api = api or APIWrapper(Database(db))

@app.route("/")
def hello():
    return "Hello"

@app.route("/api/register", methods=["POST"])
def register():
    req = request.get_json(force=True)
    username = req.get("username", None)
    password = req.get("password", None)
    try:
        with db.connect() as conn:
            conn.execute(
                "INSERT INTO User (Username, PasswordHash, AuthToken) "
                "VALUES ('" + username + "', '" + guard.hash_password(password) + "', NULL);"
            )
    except IntegrityError:
        return 'User already exists', 409
    user = guard.authenticate(username, password)
    ret = {"access_token": guard.encode_jwt_token(user)}
    return (jsonify(ret), 200)

@app.route("/api/login", methods=["POST"])
def login():
    """
    Logs a user in by parsing a POST request containing user credentials and
    issuing a JWT token.
    .. example::
       $ curl http://localhost:5000/login -X POST \
         -d '{"username":"Walter","password":"calmerthanyouare"}'
    """
    req = request.get_json(force=True)
    username = req.get("username", None)
    password = req.get("password", None)
    user = guard.authenticate(username, password)
    ret = {"access_token": guard.encode_jwt_token(user)}
    return (jsonify(ret), 200)

def keyword_count(name, keywords):
    count = 0
    for word in keywords.split(' '):
        if word.lower() in name.lower():
            count += 1
    return count

@app.route("/api/search/artist")
@flask_praetorian.auth_required
def search_artist():
    keywords = request.args.get("name").strip()
    username = flask_praetorian.current_user().identity
    results = []
    ids = set()
    with db.connect() as conn:
        for word in keywords.split(' '):
            stmt = sqlalchemy.text("SELECT a.ArtistId, ArtistName, ImageUrl, Genre, Popularity, Likes FROM Artist a LEFT JOIN ArtistLikes al ON a.ArtistId = al.ArtistId AND al.Username = :user WHERE LOWER(a.ArtistName) LIKE :lowerword LIMIT 20")
            result = conn.execute(stmt, user=username, lowerword="%"+word.lower()+"%").all()
            for row in result:
                asdict = dict(row)
                if asdict["ArtistId"] not in ids:
                    ids.add(asdict["ArtistId"])
                    results.append(asdict)
    results.sort(key = lambda x: keyword_count(x["ArtistName"], keywords), reverse=True)
    return (jsonify(results), 200)

@app.route("/api/search/album")
@flask_praetorian.auth_required
def search_album():
    keywords = request.args.get("name").strip()
    username = flask_praetorian.current_user().identity
    results = []
    ids = set()
    with db.connect() as conn:
        for word in keywords.split(' '):
            stmt = sqlalchemy.text("SELECT a.AlbumId, AlbumName, ArtistId, Genre, ImageUrl, Likes, Popularity, ReleaseDate FROM Album a LEFT JOIN AlbumLikes al ON a.AlbumId = al.AlbumId AND al.Username = :user WHERE LOWER(a.AlbumName) LIKE :lowerword LIMIT 20")
            result = conn.execute(stmt, user=username, lowerword="%"+word.lower()+"%").all()
            for row in result:
                asdict = dict(row)
                if asdict["AlbumId"] not in ids:
                    ids.add(asdict["AlbumId"])
                    results.append(asdict)
    results.sort(key = lambda x: keyword_count(x["AlbumName"], keywords), reverse=True)
    return (jsonify(results), 200)

@app.route("/api/search/track")
@flask_praetorian.auth_required
def search_track():
    keywords = request.args.get("name").strip()
    username = flask_praetorian.current_user().identity
    results = []
    ids = set()
    with db.connect() as conn:
        for word in keywords.split(' '):
            stmt = sqlalchemy.text("SELECT a.TrackId, TrackName, AlbumId, Duration, Genre, ImageURL, Likes, Popularity, ReleaseDate FROM Track a LEFT JOIN TrackLikes al ON a.TrackId = al.TrackId AND al.Username = :user WHERE LOWER(a.TrackName) LIKE :lowerword LIMIT 20")
            result = conn.execute(stmt, user=username, lowerword="%"+word.lower()+"%").all()
            for row in result:
                asdict = dict(row)
                if asdict["TrackId"] not in ids:
                    ids.add(asdict["TrackId"])
                    results.append(asdict)
    results.sort(key = lambda x: keyword_count(x["TrackName"], keywords), reverse=True)
    return (jsonify(results), 200)

@app.route("/api/recommend/artist")
@flask_praetorian.auth_required
def recommend_artist():
    req = request.get_json(force=True)
    username = req.get("username", None)

    result = None
    try:
        stmt = sqlalchemy.text("SELECT ArtistId FROM ArtistLikes WHERE Username = :usernameToCheck")
        with db.connect() as conn:
            result = conn.execute(stmt, usernameToCheck=username).first()
    except Exception as e:
        print(e)
    
    # loop through all liked songs to find average of all track properties
    avgTrackProperties = [[0, 0, 'Danceability'],[0, 0, 'Energy'],[0, 0, 'Loudness'],[0, 0, 'Speechiness'],[0, 0, 'Acousticness'],[0, 0, 'Instrumentalness'],[0, 0, 'Liveness'],[0, 0, 'Valence'],[0, 0, 'Tempo']]
    for artistId in result['ArtistId']:
        ArtistTracks = None
        try:
            stmt = sqlalchemy.text("SELECT Danceability, Energy, Loudness, Speechiness, Acousticness, Instrumentalness, Liveness, Valence, Tempo FROM Artist a NATURAL JOIN Track tr JOIN TrackProperties tp ON (tr.TrackId = tp.TrackId) WHERE ArtistId = :artistIdToCheck")
            with db.connect() as conn:
                ArtistTracks = conn.execute(stmt, artistIdToCheck=artistId).first()
        except Exception as e:
            print(e)
        
        # Update avgTrackProperties with data of current track
        for i in range(len(avgTrackProperties)):
            avgTrackProperties[i][0] = (avgTrackProperties[i][0] * avgTrackProperties[i][1] + ArtistTracks[avgTrackProperties[2]]) / (1 + avgTrackProperties[i][1])
            avgTrackProperties[i][1] += 1
    
    # Find similar songs based on avg track properties liked with a range of +- 10 (LIMIT 15)
    output = None
    try:
        stmt = sqlalchemy.text("SELECT AristName FROM Artist a NATURAL JOIN Track tr JOIN TrackProperties tp ON (tr.TrackId = tp.TrackId) WHERE Danceability BETWEEN :danceProp - 10 AND :danceProp + 10 AND Energy BETWEEN :energyProp - 10 AND :energyProp + 10 AND Loudness BETWEEN :loudProp - 10 AND :loudProp + 10 AND Speechiness BETWEEN :speechProp - 10 AND :speechProp + 10 AND Acousticness BETWEEN :acoustProp - 10 AND :acoustProp + 10 AND Instrumentalness BETWEEN :instruProp - 10 AND :instruProp + 10 AND Liveness BETWEEN :liveProp - 10 AND :liveProp + 10 AND Valence BETWEEN :valProp - 10 AND :valProp + 10 AND Tempo BETWEEN :tempoProp - 10 AND :tempoProp + 10 GROUP BY a.ArtistId LIMIT 15")
        with db.connect() as conn:
            output = conn.execute(stmt, danceProp=avgTrackProperties[0][0], energyProp=avgTrackProperties[1][0], loudProp=avgTrackProperties[2][0], speechProp=avgTrackProperties[3][0], acoustProp=avgTrackProperties[4][0], instruProp=avgTrackProperties[5][0], liveProp=avgTrackProperties[6][0], valProp=avgTrackProperties[7][0], tempoProp=avgTrackProperties[8][0]).first()
    except Exception as e:
        print(e)

    return output['ArtistName']

@app.route("/api/recommend/album")
@flask_praetorian.auth_required
def recommend_album():
    req = request.get_json(force=True)
    username = req.get("username", None)

    result = None
    try:
        stmt = sqlalchemy.text("SELECT AlbumId FROM AlbumLikes WHERE Username = :usernameToCheck")
        with db.connect() as conn:
            result = conn.execute(stmt, usernameToCheck=username).first()
    except Exception as e:
        print(e)
    
    # loop through all liked songs to find average of all track properties
    avgTrackProperties = [[0, 0, 'Danceability'],[0, 0, 'Energy'],[0, 0, 'Loudness'],[0, 0, 'Speechiness'],[0, 0, 'Acousticness'],[0, 0, 'Instrumentalness'],[0, 0, 'Liveness'],[0, 0, 'Valence'],[0, 0, 'Tempo']]
    for albumId in result['AlbumId']:
        albumTracks = None
        try:
            stmt = sqlalchemy.text("SELECT TrackProperties FROM Album a NATURAL JOIN Track tr JOIN TrackProperties tp ON (tr.TrackId = tp.TrackId) WHERE AlbumId = :albumIdToCheck")
            with db.connect() as conn:
                albumTracks = conn.execute(stmt, albumIdToCheck=albumId).first()
        except Exception as e:
            print(e)
        
        # Update avgTrackProperties with data of current track
        for i in range(len(avgTrackProperties)):
            avgTrackProperties[i][0] = (avgTrackProperties[i][0] * avgTrackProperties[i][1] + albumTracks[avgTrackProperties[2]]) / (1 + avgTrackProperties[i][1])
            avgTrackProperties[i][1] += 1
    
    # Find similar songs based on avg track properties liked with a range of +- 10 (LIMIT 15)
    output = None
    try:
        stmt = sqlalchemy.text("SELECT AlbumName FROM Album a NATURAL JOIN Track tr JOIN TrackProperties tp ON (tr.TrackId = tp.TrackId) WHERE Danceability BETWEEN :danceProp - 10 AND :danceProp + 10 AND Energy BETWEEN :energyProp - 10 AND :energyProp + 10 AND Loudness BETWEEN :loudProp - 10 AND :loudProp + 10 AND Speechiness BETWEEN :speechProp - 10 AND :speechProp + 10 AND Acousticness BETWEEN :acoustProp - 10 AND :acoustProp + 10 AND Instrumentalness BETWEEN :instruProp - 10 AND :instruProp + 10 AND Liveness BETWEEN :liveProp - 10 AND :liveProp + 10 AND Valence BETWEEN :valProp - 10 AND :valProp + 10 AND Tempo BETWEEN :tempoProp - 10 AND :tempoProp + 10 GROUP BY AlbumId LIMIT 15")
        with db.connect() as conn:
            output = conn.execute(stmt, danceProp=avgTrackProperties[0][0], energyProp=avgTrackProperties[1][0], loudProp=avgTrackProperties[2][0], speechProp=avgTrackProperties[3][0], acoustProp=avgTrackProperties[4][0], instruProp=avgTrackProperties[5][0], liveProp=avgTrackProperties[6][0], valProp=avgTrackProperties[7][0], tempoProp=avgTrackProperties[8][0]).first()
    except Exception as e:
        print(e)

    return output['AlbumName']

@app.route("/api/recommend/track")
@flask_praetorian.auth_required
def recommend_track():
    req = request.get_json(force=True)
    username = req.get("username", None)

    result = None
    try:
        stmt = sqlalchemy.text("SELECT TrackId FROM TrackLikes WHERE Username = :usernameToCheck")
        with db.connect() as conn:
            result = conn.execute(stmt, usernameToCheck=username).first()
    except Exception as e:
        print(e)
    
    # loop through all liked songs to find average of all track properties
    avgTrackProperties = [[0, 0, 'Danceability'],[0, 0, 'Energy'],[0, 0, 'Loudness'],[0, 0, 'Speechiness'],[0, 0, 'Acousticness'],[0, 0, 'Instrumentalness'],[0, 0, 'Liveness'],[0, 0, 'Valence'],[0, 0, 'Tempo']]
    for trackId in result['TrackId']:
        output = None
        try:
            stmt = sqlalchemy.text("SELECT * FROM TrackProperties WHERE TrackId = :trackIdToCheck")
            with db.connect() as conn:
                output = conn.execute(stmt, trackIdToCheck=trackId).first()
        except Exception as e:
            print(e)
        # Update avgTrackProperties with data of current track
        for i in range(len(avgTrackProperties)):
            avgTrackProperties[i][0] = (avgTrackProperties[i][0] * avgTrackProperties[i][1] + output[avgTrackProperties[2]]) / (1 + avgTrackProperties[i][1])
            avgTrackProperties[i][1] += 1
    
    # Find similar songs based on avg track properties liked with a range of +- 10 (LIMIT 15)
    output = None
    try:
        stmt = sqlalchemy.text("SELECT TrackName FROM Track NATURAL JOIN TrackProperties WHERE Danceability BETWEEN :danceProp - 10 AND :danceProp + 10 AND Energy BETWEEN :energyProp - 10 AND :energyProp + 10 AND Loudness BETWEEN :loudProp - 10 AND :loudProp + 10 AND Speechiness BETWEEN :speechProp - 10 AND :speechProp + 10 AND Acousticness BETWEEN :acoustProp - 10 AND :acoustProp + 10 AND Instrumentalness BETWEEN :instruProp - 10 AND :instruProp + 10 AND Liveness BETWEEN :liveProp - 10 AND :liveProp + 10 AND Valence BETWEEN :valProp - 10 AND :valProp + 10 AND Tempo BETWEEN :tempoProp - 10 AND :tempoProp + 10 LIMIT 15")
        with db.connect() as conn:
            output = conn.execute(stmt, danceProp=avgTrackProperties[0][0], energyProp=avgTrackProperties[1][0], loudProp=avgTrackProperties[2][0], speechProp=avgTrackProperties[3][0], acoustProp=avgTrackProperties[4][0], instruProp=avgTrackProperties[5][0], liveProp=avgTrackProperties[6][0], valProp=avgTrackProperties[7][0], tempoProp=avgTrackProperties[8][0]).first()
    except Exception as e:
        print(e)

    return output['TrackName']



@app.route("/api/interact/artist", methods=['GET', 'POST'])
@flask_praetorian.auth_required
def interact_artist():
    if request.method == 'GET':
        results = []
        with db.connect() as conn:
            stmt = sqlalchemy.text("SELECT * FROM Artist NATURAL JOIN ArtistLikes WHERE Username = :usernameToCheck")
            result = conn.execute(stmt, usernameToCheck = flask_praetorian.current_user().identity)
            for row in result:
                results.append(dict(row))
        return (jsonify(results), 200)
    req = request.get_json(force=True)
    artist_id = req.get("artist_id", None)
    interaction = req.get("interaction", None) # LIKE, DISLIKE, NEUTRAL
    username = flask_praetorian.current_user().identity
    # Insert, update or delete based on value of interaction
    result = None
    try:
        stmt = sqlalchemy.text("SELECT * FROM ArtistLikes WHERE ArtistId = :artistIdToAdd AND Username = :usernameToCheck")
        with db.connect() as conn:
            result = conn.execute(stmt, artistIdToAdd=artist_id, usernameToCheck=username).first()
    except Exception as e:
        print(e, "Trying to find artist in artist likes table")
    
    if not result:
        if interaction == "NEUTRAL":
            return '', 204
        # Insert artist into artist likes table
        like = None
        if interaction == "LIKE":
            like = True
        else:
            like = False
        try:
            stmt = sqlalchemy.text("INSERT INTO ArtistLikes VALUES (:usernameToCheck, :artistIdToAdd, :likeValue)")
            with db.connect() as conn:
                conn.execute(stmt, usernameToCheck=username, artistIdToAdd=artist_id, likeValue = like)
        except Exception as e:
            print(e, "Trying to insert artist in ArtistLikes")
    else:
        # Check if change to neutral (delete), otherwise get correct bool value (update)
        if interaction == "NEUTRAL":
            try:
                stmt = sqlalchemy.text("DELETE FROM ArtistLikes WHERE Username = :usernameToCheck AND ArtistId = :artistIdToAdd LIMIT 1")
                with db.connect() as conn:
                    conn.execute(stmt, usernameToCheck=username, artistIdToAdd=artist_id)
            except Exception as e:
                print(e)
        else:
            like = None
            if interaction == "LIKE":
                like = True
            elif interaction == "DISLIKE":
                like = False
            try:
                stmt = sqlalchemy.text("UPDATE ArtistLikes SET Likes = :likeVal WHERE Username = :usernameToCheck AND ArtistId = :artistIdToAdd LIMIT 1")
                with db.connect() as conn:
                    conn.execute(stmt, usernameToCheck=username, artistIdToAdd=artist_id, likeVal = like)
            except Exception as e:
                print(e)
    return '', 204

@app.route("/api/interact/album", methods=['GET', 'POST'])
@flask_praetorian.auth_required
def interact_album():
    if request.method == 'GET':
        results = []
        with db.connect() as conn:
            stmt = sqlalchemy.text("SELECT * FROM Album NATURAL JOIN AlbumLikes WHERE Username = :usernameToCheck")
            result = conn.execute(stmt, usernameToCheck = flask_praetorian.current_user().identity)
            for row in result:
                results.append(dict(row))
        return (jsonify(results), 200)
    req = request.get_json(force=True)
    album_id = req.get("album_id", None)
    interaction = req.get("interaction", None) # LIKE, DISLIKE, NEUTRAL
    username = flask_praetorian.current_user().identity
    # Insert, update or delete based on value of interaction
    result = None
    try:
        stmt = sqlalchemy.text("SELECT * FROM AlbumLikes WHERE AlbumId = :albumIdToAdd AND Username = :usernameToCheck")
        with db.connect() as conn:
            result = conn.execute(stmt, albumIdToAdd=album_id, usernameToCheck=username).first()
    except Exception as e:
        print(e)
    
    if not result:
        if interaction == "NEUTRAL":
            return '', 204
        # Insert artist into artist likes table
        like = None
        if interaction == "LIKE":
            like = True
        else:
            like = False
        try:
            stmt = sqlalchemy.text("INSERT INTO AlbumLikes VALUES (:usernameToCheck, :albumIdToAdd, :likeValue)")
            with db.connect() as conn:
                conn.execute(stmt, usernameToCheck=username, albumIdToAdd=album_id, likeValue = like)
        except Exception as e:
            print(e)
    else:
        # Check if change to neutral (delete), otherwise get correct bool value (update)
        if interaction == "NEUTRAL":
            try:
                stmt = sqlalchemy.text("DELETE FROM AlbumLikes WHERE Username = :usernameToCheck AND AlbumId = :albumIdToAdd LIMIT 1")
                with db.connect() as conn:
                    conn.execute(stmt, usernameToCheck=username, albumIdToAdd=album_id)
            except Exception as e:
                print(e)
        else:
            like = None
            if interaction == "LIKE":
                like = True
            elif interaction == "DISLIKE":
                like = False
            try:
                stmt = sqlalchemy.text("UPDATE AlbumLikes SET Likes = :likeVal WHERE Username = :usernameToCheck AND AlbumId = :albumIdToAdd LIMIT 1")
                with db.connect() as conn:
                    conn.execute(stmt, usernameToCheck=username, albumIdToAdd=album_id, likeVal = like)
            except Exception as e:
                print(e)
    return '', 204

@app.route("/api/interact/track", methods=['GET', 'POST'])
@flask_praetorian.auth_required
def interact_track():
    if request.method == 'GET':
        results = []
        with db.connect() as conn:
            stmt = sqlalchemy.text("SELECT * FROM Track NATURAL JOIN TrackLikes WHERE Username = :usernameToCheck")
            result = conn.execute(stmt, usernameToCheck = flask_praetorian.current_user().identity)
            for row in result:
                results.append(dict(row))
        return (jsonify(results), 200)
    req = request.get_json(force=True)
    track_id = req.get("track_id", None)
    interaction = req.get("interaction", None) # LIKE, DISLIKE, NEUTRAL
    username = flask_praetorian.current_user().identity
    # Insert, update or delete based on value of interaction
    result = None
    try:
        stmt = sqlalchemy.text("SELECT * FROM TrackLikes WHERE TrackId = :trackIdToAdd AND Username = :usernameToCheck")
        with db.connect() as conn:
            result = conn.execute(stmt, trackIdToAdd=track_id, usernameToCheck=username).first()
    except Exception as e:
        print(e)
    
    if not result:
        if interaction == "NEUTRAL":
            return '', 204
        # Insert artist into artist likes table
        like = None
        if interaction == "LIKE":
            like = True
        else:
            like = False
        try:
            stmt = sqlalchemy.text("INSERT INTO TrackLikes VALUES (:usernameToCheck, :trackIdToAdd, :likeValue)")
            with db.connect() as conn:
                conn.execute(stmt, usernameToCheck=username, trackIdToAdd=track_id, likeValue = like)
        except Exception as e:
            print(e)
    else:
        # Check if change to neutral (delete), otherwise get correct bool value (update)
        if interaction == "NEUTRAL":
            try:
                stmt = sqlalchemy.text("DELETE FROM TrackLikes WHERE Username = :usernameToCheck AND TrackId = :trackIdToAdd LIMIT 1")
                with db.connect() as conn:
                    conn.execute(stmt, usernameToCheck=username, trackIdToAdd=track_id)
            except Exception as e:
                print(e)
        else:
            like = None
            if interaction == "LIKE":
                like = True
            elif interaction == "DISLIKE":
                like = False
            try:
                stmt = sqlalchemy.text("UPDATE TrackLikes SET Likes = :likeVal WHERE Username = :usernameToCheck AND TrackId = :trackIdToAdd LIMIT 1")
                with db.connect() as conn:
                    conn.execute(stmt, usernameToCheck=username, trackIdToAdd=track_id, likeVal = like)
            except Exception as e:
                print(e)
    return '', 204


@app.route("/fill_database")
def fill_database():
    global api
    api.fill_database()
    return "Filled database."

@app.route("/artist/<artist>")
def fill_artist(artist):
    global api
    api.fill_for_artist_by_search(escape(artist))
    return f"Filled for artist {escape(artist)}"

@app.route("/api/delete", methods=["DELETE"])
def delete_artist():
    global api
    logger.error(f"Trying to delete {request.json['artist']}")
    if api.delete_artist_by_name(escape(request.json['artist'])):
        return '', 204
    else:
        return '', 404


@app.route("/api/insert", methods=["POST"])
def insert_artist():
    global api
    data = request.get_json()
    artist_name = data['artist']
    api.fill_for_artist_by_search(escape(artist_name))
    return '', 204


@app.route("/api/getAlbums")
def get_albums():
    data = request.args
    return jsonify(api.get_albums_by_attributes(data))
    #return api.get_albums_by_attributes(data)

@app.route("/api/update", methods=["PATCH"])
def update_user_like():
    global api
    data = request.get_json()
    logger.error(data)
    if api.update_user_like(data):
        return '', 204
    else:
        return '', 404

@app.route("/api/getTracks")
def get_tracks():
    data = request.args
    return api.get_tracks_by_attributes(data)

@app.route("/api/getTracksWithPopularity")
def get_tracks_with_popularity():
    global api
    return jsonify(api.get_tracks_with_popularity(request.args))

@app.route("/api/getAlbumsWithTempo")
def get_albums_with_tempo():
    global api
    return jsonify(api.get_albums_with_tempo(request.args))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
