-- Grunden med alla tables som som ska skapas.

DROP SCHEMA IF EXISTS diaper_counter;
CREATE SCHEMA diaper_counter;
USE diaper_counter;


-- table structure for adults

CREATE TABLE adults (
  adult_id INTEGER NOT NULL AUTO_INCREMENT,
  name VARCHAR(40) NOT NULL,
  age DATE NOT NULL,
  PRIMARY KEY (adult_id)
);

-- table structure for adults

CREATE TABLE baby (
  baby_id INTEGER NOT NULL AUTO_INCREMENT,
  name VARCHAR(40) NOT NULL,
  age DATE NOT NULL,
  PRIMARY KEY (baby_id)
);

CREATE TABLE change_types (
  change_id INTEGER NOT NULL AUTO_INCREMENT,
  change_type VARCHAR(15) NOT NULL CHECK (change_type IN ('poo','pee','routine')),
  PRIMARY KEY (change_id)
);

-- table structure for changes

CREATE TABLE diaper_changes (
  change_id INTEGER NOT NULL AUTO_INCREMENT,
  change_type_id INTEGER NOT NULL,
  baby_id INTEGER NOT NULL,
  accident BOOLEAN NOT NULL DEFAULT FALSE,
  adult_id INTEGER NOT NULL,
  change_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (change_id),
  FOREIGN KEY (baby_id) REFERENCES baby (baby_id) ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (adult_id) REFERENCES adults (adult_id) ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (change_type_id) REFERENCES change_types (change_id) ON DELETE RESTRICT ON UPDATE CASCADE
);
