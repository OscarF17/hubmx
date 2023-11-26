DROP DATABASE IF EXISTS HubMX;
CREATE DATABASE HubMX;
USE HubMX;

GRANT ALL PRIVILEGES ON * TO usr@localhost IDENTIFIED BY '123';
FLUSH PRIVILEGES;

CREATE TABLE Review(
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200),
    date DATETIME,
    text TEXT,
    sentiment ENUM('POS', 'NEG', 'NEU')
);

DELIMITER ..
CREATE PROCEDURE createReview(
    IN usr_name VARCHAR(200),
    IN usr_text TEXT,
    IN usr_sentiment VARCHAR(100)
)
BEGIN
    SET @d = now();
    INSERT INTO Review (name, date, text, sentiment) VALUES 
        (usr_name, @d, usr_text, usr_sentiment);
END ..
DELIMITER ;

DELIMITER ..
CREATE PROCEDURE getReviews()
BEGIN
    SELECT * FROM Review;
END ..
DELIMITER ;
