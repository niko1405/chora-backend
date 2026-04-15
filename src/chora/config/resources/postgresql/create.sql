SET default_tablespace = choraspace;

CREATE TABLE IF NOT EXISTS artist (
    id            INTEGER GENERATED ALWAYS AS IDENTITY(START WITH 1000) PRIMARY KEY,
    version       INTEGER NOT NULL DEFAULT 0,
    name          TEXT NOT NULL,
                  -- impliziter Index als B-Baum durch UNIQUE
                  -- https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-UNIQUE-CONSTRAINTS
    email         TEXT NOT NULL UNIQUE,
                  -- https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-CHECK-CONSTRAINTS
    geburtsdatum  DATE NOT NULL CHECK (geburtsdatum < current_date),
    username      TEXT,
                  -- https://www.postgresql.org/docs/current/datatype-datetime.html
    erzeugt       TIMESTAMP NOT NULL,
    aktualisert   TIMESTAMP NOT NULL
);

-- default: btree
CREATE INDEX IF NOT EXISTS artist_name_idx ON artist(name);

CREATE TABLE IF NOT EXISTS song (
    id          INTEGER GENERATED ALWAYS AS IDENTITY(START WITH 1000) PRIMARY KEY,
    titel       TEXT NOT NULL,
    erscheinungsdatum DATE NOT NULL CHECK (erscheinungsdatum <= current_date),
    dauer       INTEGER NOT NULL CHECK (dauer > 0),
    genres      JSON
);

CREATE INDEX IF NOT EXISTS song_titel_idx ON song(titel);

CREATE TABLE IF NOT EXISTS song_artist (
    song_id     INTEGER NOT NULL REFERENCES song ON DELETE CASCADE,
    artist_id   INTEGER NOT NULL REFERENCES artist ON DELETE CASCADE,
    PRIMARY KEY (song_id, artist_id)
);

CREATE INDEX IF NOT EXISTS song_artist_song_id_idx ON song_artist(song_id);
CREATE INDEX IF NOT EXISTS song_artist_artist_id_idx ON song_artist(artist_id);

CREATE TABLE IF NOT EXISTS vertrag (
    id          INTEGER GENERATED ALWAYS AS IDENTITY(START WITH 1000) PRIMARY KEY,
    startdatum  DATE NOT NULL,
    enddatum    DATE NOT NULL,
    dauer       INTEGER NOT NULL CHECK (dauer > 0),
    firma       TEXT NOT NULL,
                -- https://www.postgresql.org/docs/current/datatype-numeric.html#DATATYPE-NUMERIC-DECIMAL
                -- 12 Stellen, davon 2 Nachkommastellen
    gehalt      NUMERIC(12,2) NOT NULL CHECK (gehalt >= 0),
    artist_id   INTEGER NOT NULL UNIQUE REFERENCES artist ON DELETE CASCADE,
                -- Vertragszeitraum muss gueltig sein
    CHECK (enddatum > startdatum)
);

CREATE INDEX IF NOT EXISTS vertrag_artist_id_idx ON vertrag(artist_id);
