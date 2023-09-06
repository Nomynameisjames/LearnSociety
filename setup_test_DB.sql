DROP DATABASE BotSchedule;


CREATE DATABASE IF NOT EXISTS BotSchedule;

 -- Switch database to new database

USE BotSchedule;

-- create user if not exists and set password, privileges

  -- delete table if exist

 DROP TABLE IF EXISTS `user_info`;
  
    CREATE TABLE `user_info` (
    `ID` VARCHAR(200) NOT NULL,
    `User_name` VARCHAR(50) NOT NULL,
    `Email` VARCHAR(50) NOT NULL,
    `Password` VARCHAR(255) NOT NULL,
    `Phone_number` VARCHAR(50) NULL,
    `Created_at` VARCHAR(50) NOT NULL,
    `Updated_at` VARCHAR(50) NULL,
    `save_history` INT,
    `Rooms` INT(0),
    PRIMARY KEY (`ID`)
 );


DROP TABLE IF EXISTS `January`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
  /*!40101 SET character_set_client = utf8 */;

 CREATE TABLE `January` (
    `ID` int NOT NULL AUTO_INCREMENT,
    `user_ID` VARCHAR(200) NOT NULL,
    `Days` VARCHAR(50),
    `Course` VARCHAR(50),
    `Topic` VARCHAR(50),
    `Reminder` VARCHAR(50),
    `Target` INT,
    `Average` INT,
    `created_at` VARCHAR(50),
    `updated_at` VARCHAR(50),
    PRIMARY KEY(`ID`),
    FOREIGN KEY (`user_ID`) REFERENCES `user_info` (`ID`)
  ); 

DROP TABLE IF EXISTS `JavascriptDB`;
  
CREATE TABLE `JavascriptDB` (
      `ID` INT NOT NULL AUTO_INCREMENT,
      `Days` VARCHAR(50),
      `user_ID` VARCHAR(200) NOT NULL,
      `Course` VARCHAR(50),
      `Topic` VARCHAR(50),
      `Reminder` VARCHAR(50),
      `Target` INT DEFAULT 0,
      `Average` INT,
      `created_at` VARCHAR(50),
      `updated_at` VARCHAR(50),
      PRIMARY KEY(`ID`),
      FOREIGN KEY (`user_ID`) REFERENCES `user_info` (`ID`)
    );

DROP TABLE IF EXISTS `PythonDB`;
 

CREATE TABLE `PythonDB` (
      `ID` INT NOT NULL AUTO_INCREMENT,
      `Days` VARCHAR(50),
      `user_ID` VARCHAR(200) NOT NULL,
      `Course` VARCHAR(50),
      `Topic` VARCHAR(50),
      `Reminder` VARCHAR(50),
      `Target` INT DEFAULT 0,
      `Average` INT,
      `created_at` VARCHAR(50),
      `updated_at` VARCHAR(50),
      PRIMARY KEY(`ID`),
      FOREIGN KEY (`user_ID`) REFERENCES `user_info` (`ID`)
    );

DROP TABLE IF EXISTS `ReactDB`;

CREATE TABLE `ReactDB` (
      `ID` INT NOT NULL AUTO_INCREMENT,
      `Days` VARCHAR(50),
      `user_ID` VARCHAR(200) NOT NULL,
      `Course` VARCHAR(50),
      `Topic` VARCHAR(50),
      `Reminder` VARCHAR(50),
      `Target` INT DEFAULT 0,
      `Average` INT,
      `created_at` VARCHAR(50),
      `updated_at` VARCHAR(50),
      PRIMARY KEY(`ID`),
      FOREIGN KEY (`user_ID`) REFERENCES `user_info` (`ID`)
    );

DROP TABLE IF EXISTS `C-DB`;

CREATE TABLE `C-DB` (
      `ID` INT NOT NULL AUTO_INCREMENT,
      `Days` VARCHAR(50),
      `user_ID` VARCHAR(200) NOT NULL,
      `Course` VARCHAR(50),
      `Topic` VARCHAR(50),
      `Reminder` VARCHAR(50),
      `Target` INT DEFAULT 0,
      `Average` INT,
      `created_at` VARCHAR(50),
      `updated_at` VARCHAR(50),
      PRIMARY KEY(`ID`),
      FOREIGN KEY (`user_ID`) REFERENCES `user_info` (`ID`)
    );


