import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# DROP TABLES
staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS songplays"
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS time"

# CREATE TABLES
staging_events_table_create = (
    """
        CREATE TABLE staging_events(
            event_id INT IDENTITY(0,1),
            artist_name VARCHAR,
            auth VARCHAR,
            first_name VARCHAR,
            gender VARCHAR,
            item_in_session	INT,
            last_name VARCHAR,
            song_length	FLOAT,
            level VARCHAR,
            location VARCHAR,
            method VARCHAR,
            page VARCHAR,
            registration VARCHAR,
            session_id BIGINT,
            song_title VARCHAR,
            status INT,
            ts VARCHAR,
            user_agent TEXT,
            user_id INT,
            PRIMARY KEY (event_id)
        )
    """
)

staging_songs_table_create = (
    """
        CREATE TABLE IF NOT EXISTS staging_songs (
            num_songs INT,
            artist_id VARCHAR,
            artist_latitude FLOAT,
            artist_longitude FLOAT,
            artist_location VARCHAR,
            artist_name VARCHAR,
            song_id VARCHAR,
            title VARCHAR,
            duration FLOAT,
            year INT,
            PRIMARY KEY(song_id)
        )
    """
)

songplay_table_create = (
    """
        CREATE TABLE IF NOT EXISTS songplays (
            songplay_id INT IDENTITY(0,1),
            start_time TIMESTAMP REFERENCES time(start_time),
            user_id INT REFERENCES users(user_id),
            level VARCHAR,
            song_id VARCHAR REFERENCES songs(song_id),
            artist_id VARCHAR REFERENCES artists(artist_id),
            session_id INT,
            location VARCHAR,
            user_agent VARCHAR,
            PRIMARY KEY (songplay_id)
        )
    """
)

user_table_create = (
    """
        CREATE TABLE IF NOT EXISTS users (
            user_id INT,
            first_name VARCHAR,
            last_name VARCHAR,
            gender CHAR,
            level VARCHAR,
            PRIMARY KEY (user_id)
        )
    """
)

song_table_create = (
    """
        CREATE TABLE IF NOT EXISTS songs (
            song_id VARCHAR,
            title VARCHAR,
            artist_id VARCHAR,
            year INT,
            duration FLOAT,
            PRIMARY KEY (song_id)
        );
    """
)

artist_table_create = (
    """
        CREATE TABLE IF NOT EXISTS artists (
            artist_id VARCHAR,
            name VARCHAR,
            location VARCHAR,
            latitude FLOAT,
            longitude FLOAT,
            PRIMARY KEY (artist_id)
        )
    """
)

time_table_create = (
    """
        CREATE TABLE IF NOT EXISTS time (
            start_time TIMESTAMP,
            hour INT,
            day INT,
            week INT,
            month INT,
            year INT,
            weekday VARCHAR,
            PRIMARY KEY (start_time)
        )
    """
)

# STAGING TABLES
"""
- Turn OFF COMPUPDATE, STATUPDATE to speed up COPY process
- Load data from JSON Arrays Using a JSONPaths file (LOG_JSONPATH)
"""
staging_events_copy = (
    """
        copy staging_events from {}
        credentials 'aws_iam_role={}'
        region 'us-west-2'
        COMPUPDATE OFF STATUPDATE OFF
        JSON {}
    """
).format(
    config.get('S3', 'LOG_DATA'),
    config.get('IAM_ROLE', 'ARN'),
    config.get('S3', 'LOG_JSONPATH'))

staging_songs_copy = (
    """
        copy staging_songs from {}
        credentials 'aws_iam_role={}'
        region 'us-west-2'
        COMPUPDATE OFF STATUPDATE OFF
        JSON 'auto'
    """
).format(
    config.get('S3', 'SONG_DATA'),
    config.get('IAM_ROLE', 'ARN'))

# FINAL TABLES
"""
- Only consider page = NextSong
- Include AND condition to prevent adding duplicates
"""
songplay_table_insert = (
    """
        INSERT INTO songplays (
            start_time,
            user_id,
            level,
            song_id,
            artist_id,
            session_id,
            location,
            user_agent
        )
            SELECT DISTINCT
                TIMESTAMP 'epoch' + ts/1000 *INTERVAL '1 second' as start_time,
                e.user_id,
                e.level,
                s.song_id,
                s.artist_id,
                e.session_id,
                e.location,
                e.user_agent
            FROM staging_events e, staging_songs s
            WHERE e.page = 'NextSong'
            AND e.song_title = s.title
            AND user_id NOT IN (SELECT DISTINCT s.user_id FROM songplays s WHERE s.user_id = user_id
                               AND s.start_time = start_time AND s.session_id = session_id )
    """
)

user_table_insert = (
    """
        INSERT INTO users (
            user_id,
            first_name,
            last_name,
            gender,
            level
        )
        SELECT DISTINCT
            user_id,
            first_name,
            last_name,
            gender,
            level
        FROM
            staging_events
        WHERE
            page = 'NextSong'
        AND user_id NOT IN (SELECT DISTINCT user_id FROM users)
    """
)

song_table_insert = (
    """
        INSERT INTO songs (
            song_id,
            title,
            artist_id,
            year,
            duration
        )
        SELECT DISTINCT
            song_id,
            title,
            artist_id,
            year,
            duration
        FROM
            staging_songs
        WHERE song_id NOT IN (SELECT DISTINCT song_id FROM songs)
    """
)

artist_table_insert = (
    """
        INSERT INTO artists (
            artist_id,
            name,
            location,
            latitude,
            longitude)
        SELECT DISTINCT
            artist_id,
            artist_name,
            artist_location,
            artist_latitude,
            artist_longitude
        FROM
            staging_songs
        WHERE
            artist_id NOT IN (SELECT DISTINCT artist_id FROM artists)
    """
)

time_table_insert = (
    """
        INSERT INTO time (
            start_time,
            hour,
            day,
            week,
            month,
            year,
            weekday
        )
        SELECT
            start_time,
            EXTRACT(hr from start_time) AS hour,
            EXTRACT(d from start_time) AS day,
            EXTRACT(w from start_time) AS week,
            EXTRACT(mon from start_time) AS month,
            EXTRACT(yr from start_time) AS year,
            EXTRACT(dow from start_time) AS weekday
        FROM (
            SELECT
                DISTINCT TIMESTAMP 'epoch' + ts/1000 *INTERVAL '1 second' as start_time
            FROM
                staging_events
            )
        WHERE
            start_time NOT IN (SELECT DISTINCT start_time FROM time)
    """
)

# QUERY LISTS
create_table_queries = [
    staging_events_table_create, staging_songs_table_create,
    user_table_create, song_table_create, artist_table_create,
    time_table_create, songplay_table_create]
drop_table_queries = [
    staging_events_table_drop, staging_songs_table_drop,
    songplay_table_drop, user_table_drop, song_table_drop,
    artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
