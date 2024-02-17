CREATE TABLE races (
    id serial PRIMARY KEY,
    datasport_id integer NOT NULL,
    name varchar(256) NOT NULL,
    distance double precision NOT NULL
);

CREATE TABLE participants (
    id serial PRIMARY KEY,
    name varchar(256) NOT NULL,
    age integer NOT NULL,
    gender char(1),
    finish_time integer,
    finished boolean NOT NULL,
    started boolean NOT NULL,
    race_id integer NOT NULL
);
