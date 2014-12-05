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

INSERT INTO twitter_credentials VALUES(
    'iit_cs549_p',
    '2898195857-Cr7Z1yV4HmgAu3OqI5hdIssuhmo3K9ManQ8LC2b',
    'YUeanihKiwGkRV6lPLixEyzxq9v5ugrwFjjetoapzLncC',
    'jDHthtAE82TMhaCztUZNrNTcn',
    'sDgbfm4OZB0xKPYpx0qQFeaFel1Xvq8aSqloMyZw40Ag9t82vv'
);

END;