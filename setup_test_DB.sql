 -- delete database if exixt

DROP DATABASE IF EXISTS BotSchedule;

 -- Creates database if not exist

CREATE DATABASE IF NOT EXISTS BotSchedule;

 -- Switch database to new database

USE BotSchedule_test_db;

-- create user if not exists and set password, privileges

/*CREATE USER IF NOT EXISTS 'BotSchedule'@'localhost';
SET PASSWORD FOR 'BotSchedule'@'localhost' = 'BotSchedule';
GRANT ALL PRIVILEGES ON BotSchedule.* TO 'BotSchedule'@'localhost';
GRANT SELECT ON performance_schema.* TO 'BotSchedule'@'localhost'; */

  -- Table structure for table `cities`

  -- delete table if exist

 DROP TABLE IF EXISTS `user_info`;
  
    CREATE TABLE `user_info` (
    `id` VARCHAR(200) NOT NULL,
    `User_name` VARCHAR(50) NOT NULL,
    `Email` VARCHAR(50) NOT NULL,
    `Password` VARCHAR(255) NOT NULL,
    `Created_at` VARCHAR(50) NOT NULL,
    `Updated_at` VARCHAR(50) NULL,
    PRIMARY KEY (`id`)
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
    FOREIGN KEY (`user_ID`) REFERENCES `user_info` (`id`)
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
      FOREIGN KEY (`user_ID`) REFERENCES `user_info` (`id`)
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
      FOREIGN KEY (`user_ID`) REFERENCES `user_info` (`id`)
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
      FOREIGN KEY (`user_ID`) REFERENCES `user_info` (`id`)
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
      FOREIGN KEY (`user_ID`) REFERENCES `user_info` (`id`)
    );


