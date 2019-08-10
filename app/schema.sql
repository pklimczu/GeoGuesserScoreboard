DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS game;
DROP TABLE IF EXISTS result;
DROP TABLE IF EXISTS link;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    uuid TEXT NOT NULL
);

CREATE TABLE game (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    datestamp DATE NOT NULL DEFAULT CURRENT_DATE,
    map TEXT,
    winner TEXT,
    uuid TEXT NOT NULL,
    FOREIGN KEY (winner) REFERENCES user (username)
);

CREATE TABLE result (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_uuid TEXT NOT NULL,
    game_uuid TEXT NOT NULL,
    score INTEGER NOT NULL,
    FOREIGN KEY (user_uuid) REFERENCES user (uuid),
    FOREIGN KEY (game_uuid) REFERENCES game (uuid)
);

CREATE TABLE link (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_uuid TEXT NOT NULL,
    map_hash TEXT NOT NULL,
    game_hash TEXT NOT NULL,
    FOREIGN KEY (game_uuid) REFERENCES game (uuid)
);