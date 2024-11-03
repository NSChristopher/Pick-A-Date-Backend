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
  `start_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `lon` DECIMAL(10,8) NULL,
  `lat` DECIMAL(10,8) NULL,
  `uuid` VARCHAR(45) NOT NULL,
  `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
  PRIMARY KEY (`event_id`),
  UNIQUE INDEX `event_id` (`event_id` ASC) VISIBLE);

-- -----------------------------------------------------
-- Table `PickADateDB`.`user`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `PickADateDB`.`user` ;

CREATE TABLE IF NOT EXISTS `PickADateDB`.`user` (
  `user_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `event_id` INT UNSIGNED NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  `email` VARCHAR(254) NOT NULL,
  `lat` DECIMAL(10,8) NULL,
  `lon` DECIMAL(10,8) NULL,
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
  `user_id` INT UNSIGNED NOT NULL,
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
