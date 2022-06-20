CREATE DATABASE IF NOT EXISTS main;

CREATE TABLE main.users
(
    userId      INTEGER UNIQUE AUTO_INCREMENT PRIMARY KEY,
    userEmail   VARCHAR(200) NOT NULL UNIQUE,
    lastAlerted TIMESTAMP # unix timestamp

);

CREATE TABLE main.plumePlatforms
(
    platformId                INTEGER UNIQUE AUTO_INCREMENT PRIMARY KEY,
    plumeInternalPlatformId   INTEGER UNIQUE,
    plumePlatformSerialNumber VARCHAR(17) UNIQUE,
    plumePlatformEmail        VARCHAR(50),
    plumePlatformPassword     VARCHAR(50)
);

CREATE TABLE main.ownedPlatforms
(
    platformId INTEGER,
    userID     INTEGER,
    FOREIGN KEY (platformId) REFERENCES plumePlatforms (platformId),
    FOREIGN KEY (userID) REFERENCES users (userId)

);
