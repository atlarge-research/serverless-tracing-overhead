CREATE DATABASE world;

-- CREATE USER dbuser WITH ENCRYPTED PASSWORD 'dbpassword';
-- GRANT ALL PRIVILEGES ON DATABASE world TO dbuser;

\c world;

CREATE TABLE World (
    id SERIAL PRIMARY KEY,
    randomNumber INT NOT NULL
);

INSERT INTO World (randomNumber)
SELECT floor(random() * 10000 + 1)::int
FROM generate_series(1, 10000);

-- TechEmpower settings
CREATE DATABASE hello_world;
\c hello_world;

CREATE TABLE World (
    id SERIAL PRIMARY KEY,
    randomNumber INT NOT NULL
);

INSERT INTO World (randomNumber)
SELECT floor(random() * 10000 + 1)::int
FROM generate_series(1, 10000);