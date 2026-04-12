PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS operation_counts;
DROP TABLE IF EXISTS operations;
DROP TABLE IF EXISTS surgeon_demographics;
DROP TABLE IF EXISTS specialties;
DROP TABLE IF EXISTS campuses;
DROP TABLE IF EXISTS languages;
DROP TABLE IF EXISTS surgeon_languages;

CREATE TABLE specialties(
specialty_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
specialty_name TEXT UNIQUE NOT NULL
);

CREATE TABLE campuses(
campus_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
campus_name TEXT UNIQUE NOT NULL
);


CREATE TABLE surgeon_demographics (
  surgeon_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  first_name TEXT,
  last_name TEXT,
  gender TEXT,
  specialty_id INTEGER NOT NULL,
  campus_id INTEGER NOT NULL,
  office_phone TEXT,
  FOREIGN KEY (specialty_id) REFERENCES specialties(specialty_id),
  FOREIGN KEY (campus_id) REFERENCES campuses(campus_id)
);

CREATE TABLE operations (
operation_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
operation_name TEXT UNIQUE NOT NULL
);

CREATE TABLE operation_counts(
operation_id INTEGER NOT NULL,
surgeon_id INTEGER NOT NULL,
count INTEGER,
PRIMARY KEY(operation_id, surgeon_id),
FOREIGN KEY(operation_id) REFERENCES operations(operation_id),
FOREIGN KEY (surgeon_id) REFERENCES surgeon_demographics(surgeon_id)
);