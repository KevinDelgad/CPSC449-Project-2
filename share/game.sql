PRAGMA foreign_KEYs=ON;
BEGIN TRANSACTION;
CREATE TABLE games (
    gamesid INTEGER PRIMARY KEY AUTOINCREMENT,
    answerid INTEGER,
    gameid INTEGER,
    username VARCHAR(25) NOT NULL,
    FOREIGN KEY (answerid) REFERENCES answer(answerid),
    FOREIGN KEY(gameid) REFERENCES game(gameid)
);

CREATE TABLE game(
    gameid INTEGER PRIMARY KEY AUTOINCREMENT,
    guesses INTEGER,
    gstate VARCHAR(12)
);

CREATE TABLE guess(
    guessid INTEGER PRIMARY KEY AUTOINCREMENT,
    gameid INTEGER,
    guessedword VARCHAR(5),
    accuracy VARCHAR(5),
    FOREIGN KEY(gameid) REFERENCES game(gameid)
);

CREATE INDEX idx_user_games ON games (username, gameid);

CREATE INDEX idx_game_guesses ON guess (guessid, guessedword, accuracy);
