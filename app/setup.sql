CREATE DATABASE IF NOT EXISTS main;
USE main;

DROP TABLE IF EXISTS owners;
DROP TABLE IF EXISTS sensors;
DROP TABLE IF EXISTS plumePlatforms;
DROP TABLE IF EXISTS ownedPlatforms;

CREATE TABLE owners
(
    ownerId     INTEGER UNIQUE AUTO_INCREMENT PRIMARY KEY,
    ownerEmail  VARCHAR(200) NOT NULL UNIQUE,
    lastAlerted TIMESTAMP # unix timestamp
);

CREATE TABLE sensors
(
    sensorId   INTEGER UNIQUE AUTO_INCREMENT PRIMARY KEY,
    externalId INTEGER UNIQUE,
    ownerId INTEGER,
    sensorName VARCHAR(100),
    FOREIGN KEY (ownerId) REFERENCES owners (ownerId)
);

CREATE TABLE plumePlatforms
(
    sensorId     INTEGER,
    serialNumber VARCHAR(17) UNIQUE,
    email        VARCHAR(50),
    password     VARCHAR(50),
    FOREIGN KEY (sensorId) REFERENCES sensors (sensorId)
);

