CREATE DATABASE world;

\c world;

CREATE TABLE World (
    id SERIAL PRIMARY KEY,
    randomNumber INT NOT NULL
);

INSERT INTO World (randomNumber)
SELECT floor(random() * 10000 + 1)::int
FROM generate_series(1, 10000);
