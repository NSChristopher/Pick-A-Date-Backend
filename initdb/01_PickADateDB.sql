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
  `event_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `event_name` VARCHAR(45) NOT NULL,
  `description` VARCHAR(255) NULL,
  `date_created` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `min_date` DATE NOT NULL DEFAULT DATE_ADD(CURRENT_DATE, INTERVAL 1 DAY),
  `max_date` DATE NOT NULL DEFAULT DATE_ADD(CURRENT_DATE, INTERVAL 30 DAY),
  `uuid` VARCHAR(45) NOT NULL,
  `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
  PRIMARY KEY (`event_id`),
  UNIQUE INDEX `event_id` (`event_id` ASC) VISIBLE);

-- -----------------------------------------------------
-- Table `PickADateDB`.`address`
-- -----------------------------------------------------

DROP TABLE IF EXISTS `PickADateDB`.`address` (
  `address_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `entity_type` ENUM('event', 'user') NOT NULL,
  `entity_id` INT UNSIGNED NOT NULL,
  `address_name` VARCHAR(255) NOT NULL,
  `street_line_1` VARCHAR(255) NOT NULL,
  `street_line_2` VARCHAR(255) NULL,
  `city` VARCHAR(255) NOT NULL,
  `state_or_province` VARCHAR(255) NOT NULL,
  `country_code` VARCHAR(2) NOT NULL,
  `postal_code` VARCHAR(20) NOT NULL,
  `latitude` DECIMAL(9,6) NULL,
  `longitude` DECIMAL(9,6) NULL,
  PRIMARY KEY (`address_id`),
  INDEX `entity_id_idx` (`entity_type`, `entity_id`)
);

-- -----------------------------------------------------
-- Table `PickADateDB`.`user`

-- -----------------------------------------------------
DROP TABLE IF EXISTS `PickADateDB`.`user` ;

CREATE TABLE IF NOT EXISTS `PickADateDB`.`user` (
  `user_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `event_id` INT UNSIGNED NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  `phone` VARCHAR(64) NOT NULL,
  `postal_code` VARCHAR(20) NULL,
  `icon_path` VARCHAR(45) NULL,
  `color` VARCHAR(45) NULL,
  `is_driver` BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (`user_id`),
  UNIQUE INDEX `user_id` (`user_id` ASC) VISIBLE,
  INDEX `event_id_idx` (`event_id` ASC) VISIBLE,
  CONSTRAINT `user_event_id`
    FOREIGN KEY (`event_id`)
    REFERENCES `PickADateDB`.`event` (`event_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);

-- -----------------------------------------------------
-- Table `PickADateDB`.`date`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `PickADateDB`.`date` ;

CREATE TABLE IF NOT EXISTS `PickADateDB`.`date` (
  `date_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `event_id` INT UNSIGNED NOT NULL,
  `user_id` INT UNSIGNED,
  `date` DATE NOT NULL,
  `is_blocked` BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (`date_id`),
  UNIQUE INDEX `date_id` (`date_id` ASC) VISIBLE,
  INDEX `event_id_idx` (`event_id` ASC) VISIBLE,
  INDEX `user_id_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `date_event_id`
    FOREIGN KEY (`event_id`)
    REFERENCES `PickADateDB`.`event` (`event_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `date_user_id`
    FOREIGN KEY (`user_id`)
    REFERENCES `PickADateDB`.`user` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `one_user_id_per_date`
    UNIQUE (`event_id`, `date`, `user_id`));


-- ------------------------------------------------
-- Triggers
-- ------------------------------------------------

DELIMITER $$
CREATE TRIGGER `PickADateDB`.`event_ON_DELETE` BEFORE DELETE ON `PickADateDB`.`event`
FOR EACH ROW
BEGIN
    DELETE FROM `PickADateDB`.`user` WHERE `event_id` = OLD.`event_id`;
    DELETE FROM `PickADateDB`.`date` WHERE `event_id` = OLD.`event_id`;
    DELETE FROM `PickADateDB`.`address` WHERE `event_id` = OLD.`event_id`;
END$$
DELIMITER ;