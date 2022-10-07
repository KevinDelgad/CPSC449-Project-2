PRAGMA foreign_KEYs=ON;
BEGIN TRANSACTION;
CREATE TABLE user( 
    userid INTEGER PRIMARY KEY AUTOINCREMENT, 
    fname TEXT NOT NULL, 
    lname TEXT NOT NULL,
    username VARCHAR(25) NOT NULL, 
    passwrd VARCHAR(20) NOT NULL, 
    UNIQUE(username)
);

CREATE TABLE games (
    gamesid INTEGER PRIMARY KEY AUTOINCREMENT,
    userid INTEGER,
    answerid INTEGER,
    gameid INTEGER,
    FOREIGN KEY(userid) REFERENCES user(userid),
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

CREATE TABLE answer(
    answerid INTEGER PRIMARY KEY AUTOINCREMENT,
    answord VARCHAR(5)
);

CREATE TABLE valid_word(
    valid_id INTEGER PRIMARY KEY AUTOINCREMENT,
    valword VARCHAR(5)
);
COMMIT;
