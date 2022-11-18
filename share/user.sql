PRAGMA foreign_KEYs=ON;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS user;
CREATE TABLE user(
    username VARCHAR(25) PRIMARY KEY NOT NULL,
    passwrd VARCHAR(20) NOT NULL,
    fname TEXT NOT NULL,
    lname TEXT NOT NULL,
    UNIQUE(username)
);

CREATE INDEX idx_user ON user(username, passwrd);
-- SELECT TABLE user USING COVERING INDEX sqlite_autoindex_user_1 (username=?);
-- SELECT  user USING INDEX sqlite_autoindex_user_1 (username=?);

COMMIT;
