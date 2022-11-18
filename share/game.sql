PRAGMA foreign_KEYs=ON;
BEGIN TRANSACTION;

CREATE TABLE games (
    gamesid INTEGER PRIMARY KEY,
    username INTEGER,
    answerid INTEGER,
    gameid UUID,
    FOREIGN KEY (answerid) REFERENCES answer(answerid),
    FOREIGN KEY(gameid) REFERENCES game(gameid)
);

CREATE INDEX idx_user_games
ON games (username, gameid);

CREATE TABLE game(
    gameid UUID PRIMARY KEY,
    guesses INTEGER,
    gstate VARCHAR(12)
);

CREATE TABLE guess(
    guessid INTEGER PRIMARY KEY AUTOINCREMENT,
    gameid UUID,
    guessedword VARCHAR(5),
    accuracy VARCHAR(5),
    FOREIGN KEY(gameid) REFERENCES game(gameid)
);

CREATE INDEX idx_game_guesses
ON guess (guessid, guessedword, accuracy);

CREATE TABLE answer(
    answerid INTEGER PRIMARY KEY AUTOINCREMENT,
    answord VARCHAR(5)
);

CREATE TABLE valid_word(
    valid_id INTEGER PRIMARY KEY AUTOINCREMENT,
    valword VARCHAR(5)
);

SCAN TABLE answer;
USE TEMP B-TREE FOR ORDER BY;

CREATE INDEX games_idx_a114f231 ON games(username, answerid);

SEARCH TABLE games USING COVERING INDEX games_idx_a114f231 (username=? AND answerid=?);

CREATE INDEX games_idx_8df6ac78 ON games(gameid, answerid);
CREATE INDEX answer_idx_0382b0a6 ON answer(answord);

SEARCH TABLE answer AS a USING COVERING INDEX answer_idx_0382b0a6 (answord=?);
CORRELATED SCALAR SUBQUERY 1;
SEARCH TABLE games USING COVERING INDEX games_idx_8df6ac78 (gameid=? AND answerid=?);

CREATE INDEX valid_word_idx_0420916f ON valid_word(valword);

SEARCH TABLE valid_word USING COVERING INDEX valid_word_idx_0420916f (valword=?);

SEARCH TABLE game USING INTEGER PRIMARY KEY (rowid=?);

CREATE INDEX games_idx_8df6ac78 ON games(gameid, answerid);

SEARCH TABLE games AS g USING COVERING INDEX games_idx_8df6ac78 (gameid=?);
SEARCH TABLE answer AS a USING INTEGER PRIMARY KEY (rowid=?);

CREATE INDEX game_idx_0069bed0 ON game(gstate);

SEARCH TABLE game AS a USING INDEX game_idx_0069bed0 (gstate=? AND rowid=?);
LIST SUBQUERY 1;
SEARCH TABLE games USING COVERING INDEX idx_user_games (username=?);

CREATE INDEX guess_idx_0067de6f ON guess(gameid);

SEARCH TABLE game AS b USING INTEGER PRIMARY KEY (rowid=?);
SEARCH TABLE guess AS a USING INDEX guess_idx_0067de6f (gameid=?);

COMMIT;
