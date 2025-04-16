-- -----------------------------------------------------
-- Schema PickADateDB
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `PickADateDB` ;

-- -----------------------------------------------------
-- Schema PickADateDB
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `PickADateDB` DEFAULT CHARACTER SET utf8 ;
USE `PickADateDB` ;

-- -----------------------------------------------------
-- Table `PickADateDB`.`event`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `PickADateDB`.`event` ;

CREATE TABLE IF NOT EXISTS `PickADateDB`.`event` (
  `event_uuid` VARCHAR(45) NOT NULL PRIMARY KEY,
  `event_name` VARCHAR(45) NOT NULL,
  `description` VARCHAR(255) NULL,
  `date_created` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `min_date` DATE NOT NULL,
  `max_date` DATE NOT NULL,
  `is_active` BOOLEAN NOT NULL DEFAULT TRUE
);

-- -----------------------------------------------------
-- Table `PickADateDB`.`access_token`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `PickADateDB`.`access_token` ;

CREATE TABLE IF NOT EXISTS `PickADateDB`.`access_token` (
  `token` VARCHAR(64) NOT NULL PRIMARY KEY,
  `event_uuid` VARCHAR(45) NOT NULL,
  `account_id` INT UNSIGNED NOT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX `event_uuid_idx` (`event_uuid`),
  CONSTRAINT `token_event_fk`
    FOREIGN KEY (`event_uuid`)
    REFERENCES `PickADateDB`.`event` (`event_uuid`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);


-- -----------------------------------------------------
-- Table `PickADateDB`.`event_address`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `PickADateDB`.`event_address`;

CREATE TABLE IF NOT EXISTS `PickADateDB`.`event_address` (
  `event_address_id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `event_uuid` VARCHAR(45) NOT NULL,
  `address_name` VARCHAR(255) NOT NULL,
  `street_line_1` VARCHAR(255) NOT NULL,
  `street_line_2` VARCHAR(255) NULL,
  `city` VARCHAR(255) NOT NULL,
  `state_or_province` VARCHAR(255) NOT NULL,
  `country_code` VARCHAR(2) NOT NULL,
  `postal_code` VARCHAR(20) NOT NULL,
  `latitude` DECIMAL(9,6) NULL,
  `longitude` DECIMAL(9,6) NULL,
  CONSTRAINT `event_address_event_uuid`
    FOREIGN KEY (`event_uuid`)
    REFERENCES `PickADateDB`.`event` (`event_uuid`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- -----------------------------------------------------
-- Table `PickADateDB`.`account`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `PickADateDB`.`account` ;

CREATE TABLE IF NOT EXISTS `PickADateDB`.`account` (
  `account_id` VARCHAR(45) NOT NULL PRIMARY KEY,
  `email` VARCHAR(255) NOT NULL UNIQUE,
  `password_hash` VARCHAR(255) NOT NULL,
  `first_name` VARCHAR(100) NOT NULL,
  `last_name` VARCHAR(100) NOT NULL,
  `phone` VARCHAR(64),
  `postal_code` VARCHAR(20),
  `icon_path` VARCHAR(255),
  `color` VARCHAR(45),
  `is_active` BOOLEAN DEFAULT TRUE,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
  UNIQUE (`email`)
);

-- -----------------------------------------------------
-- Table `PickADateDB`.`participant`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `PickADateDB`.`participant` ;

CREATE TABLE IF NOT EXISTS `PickADateDB`.`participant` (
  `participant_id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `event_uuid` VARCHAR(45) NOT NULL,
  `account_id` INT UNSIGNED NULL,
  `name` VARCHAR(100) NOT NULL,
  `phone` VARCHAR(64),
  `postal_code` VARCHAR(20),
  `icon_path` VARCHAR(255),
  `color` VARCHAR(45),
  `is_driver` BOOLEAN DEFAULT FALSE,
  `role` ENUM('organizer', 'participant') NOT NULL DEFAULT 'participant',
  UNIQUE(event_uuid, phone),
  FOREIGN KEY (event_uuid) REFERENCES event(event_uuid),
  FOREIGN KEY (account_id) REFERENCES account(account_id)
);

-- -----------------------------------------------------
-- Table `PickADateDB`.`date`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `PickADateDB`.`date` ;

CREATE TABLE IF NOT EXISTS `PickADateDB`.`date` (
  `date_id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `event_uuid` VARCHAR(45) NOT NULL,
  `participant_id` INT UNSIGNED NOT NULL,
  `date` DATE NOT NULL,
  `availability_level` TINYINT NOT NULL DEFAULT 0, -- 0: Available, 1: Preferred, 2: Unavailable
  INDEX `event_uuid_idx` (`event_uuid` ASC) VISIBLE,
  INDEX `participant_id_idx` (`participant_id` ASC) VISIBLE,
  CONSTRAINT `date_event_uuid`
    FOREIGN KEY (`event_uuid`)
    REFERENCES `PickADateDB`.`event` (`event_uuid`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `date_participant_id`
    FOREIGN KEY (`participant_id`)
    REFERENCES `PickADateDB`.`participant` (`participant_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `one_participant_id_per_date`
    UNIQUE (`event_uuid`, `participant_id`, `date`),
  CHECK (`availability_level` IN (0, 1, 2)) -- restricts availability level to 0, 1, or 2
);


-- ------------------------------------------------
-- Triggers
-- ------------------------------------------------

DELIMITER $$
CREATE TRIGGER `event_ON_DELETE` BEFORE DELETE ON `PickADateDB`.`event`
FOR EACH ROW
BEGIN
    DELETE FROM `PickADateDB`.`event_address` WHERE `event_uuid` = OLD.event_uuid;
END$$
DELIMITER ;