CREATE DATABASE smart_team_finder;

USE smart_team_finder;

CREATE TABLE developers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    hackerrank_username VARCHAR(100),
    skills TEXT,
    experience_level VARCHAR(50),
    preferred_role VARCHAR(100)
);


CREATE TABLE teams (
    id INT AUTO_INCREMENT PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL,
    description TEXT,
    required_skills TEXT,
    team_size INT,
    created_by INT NOT NULL,
    FOREIGN KEY (created_by) REFERENCES developers(id)
);

CREATE TABLE team_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    team_id INT NOT NULL,
    developer_id INT NOT NULL,
    role VARCHAR(100),
    FOREIGN KEY (team_id) REFERENCES teams(id),
    FOREIGN KEY (developer_id) REFERENCES developers(id),
    UNIQUE (team_id, developer_id)
);

SELECT * FROM developers;

DELETE FROM developers
WHERE email = 'amani@gmail.com';

INSERT IGNORE INTO team_members (team_id, developer_id, role)
SELECT id, created_by, 'Team Leader'
FROM teams;



CREATE TABLE team_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    team_id INT NOT NULL,
    developer_id INT NOT NULL,
    status VARCHAR(20) DEFAULT 'Pending',
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (team_id) REFERENCES teams(id),
    FOREIGN KEY (developer_id) REFERENCES developers(id),

    UNIQUE (team_id, developer_id)
);

select * from team_requests;

select * from team_members;
SELECT * FROM teams;

SELECT team_id, COUNT(*) AS total_members
FROM team_members
GROUP BY team_id;


USE smart_team_finder;
SET SQL_SAFE_UPDATES = 0;
START TRANSACTION;

DELETE FROM team_requests;

DELETE FROM team_members;

DELETE FROM teams;

DELETE FROM developers;

COMMIT;


ALTER TABLE developers AUTO_INCREMENT = 1;
ALTER TABLE teams AUTO_INCREMENT = 1;
ALTER TABLE team_members AUTO_INCREMENT = 1;
ALTER TABLE team_requests AUTO_INCREMENT = 1;

SELECT COUNT(*) FROM developers;
SELECT COUNT(*) FROM teams;
SELECT COUNT(*) FROM team_members;
SELECT COUNT(*) FROM team_requests;