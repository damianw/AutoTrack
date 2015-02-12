BEGIN TRANSACTION;
CREATE TABLE people (
	id PRIMARY KEY,
  resident BOOLEAN, first_name TEXT, last_name TEXT
, home_when_phone BOOLEAN, home_when_laptop BOOLEAN, home_when_desktop BOOLEAN, home_when_tablet BOOLEAN);
CREATE TABLE `history` (
	`timestamp`	DATETIME,
	`devices_id`	INTEGER,
	PRIMARY KEY(timestamp, devices_id),
	FOREIGN KEY(`devices_id`) REFERENCES devices ( id )
);
CREATE TABLE devices (
	id PRIMARY KEY, people_id INTEGER, device_type TEXT, mac TEXT, hostname TEXT,
  FOREIGN KEY(people_id) REFERENCES people(id)
);
COMMIT;
