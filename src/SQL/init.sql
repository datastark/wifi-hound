BEGIN;

CREATE TABLE access_points(
    Mac TEXT,
    Ssid TEXT,
    LastSeen DATETIME
);

CREATE TABLE hound_config(
    SetTime DATETIME,
    Mode TEXT,
    Args TEXT
);

INSERT INTO hound_config VALUES('2014-01-01 00:00:00', 'SCAN', '');

CREATE TABLE mac_addresses(
    Mac TEXT,
    LastSeen DATETIME,
    State TEXT,
    StateDelta INT
);

CREATE TABLE twitter_credentials(
    Owner TEXT,
    AccessTokenKey TEXT,
    AccessTokenSecret TEXT,
    ConsumerKey TEXT,
    ConsumerSecret TEXT
);

END;