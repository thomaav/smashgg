CREATE TABLE IF NOT EXISTS whomst(
       display_name VARCHAR NOT NULL,
       connect_code VARCHAR NOT NULL,
       ip_address VARCHAR NOT NULL,
       region VARCHAR NOT NULL,
       time_added TIMESTAMP NOT NULL,
       note VARCHAR,
       UNIQUE(display_name, connect_code, ip_address)
);
