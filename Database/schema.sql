-- SQLite Schema

-- One database file (weather_report.db) shared by every component:
--   C3 librosa extractor   -> writes audio_features
--   C4 labelling tool      -> writes raters, human_ratings
--   C5 vibe model / CLAP   -> writes clap_embeddings, song_scores
--   C6 playlist assembler  -> reads songs + song_scores, writes playlists
--   D5 tempo validation    -> writes tempo_checks


PRAGMA foreign_keys = ON;

-- 1. Songs: one row per audio file in the library

CREATE TABLE IF NOT EXISTS songs (
    song_id INTEGER PRIMARY KEY,
    file_path TEXT NOT NULL UNIQUE,
    title TEXT,
    artist TEXT,
    duration_sec REAL NOT NULL CHECK (duration_sec > 0)
);

-- 2. Objective audio features from librosa. One row per song.

CREATE TABLE IF NOT EXISTS audio_features (
    song_id INTEGER PRIMARY KEY REFERENCES songs(song_id) ON DELETE CASCADE,
    tempo_bpm REAL,
    loudness_db REAL,
    music_key INTEGER CHECK (music_key BETWEEN 0 AND 11),
    mode INTEGER CHECK (mode IN (0, 1)), --major or minor
    -- spectral features
    spectral_centroid_mean REAL,      
    spectral_bandwidth_mean REAL,
    spectral_rolloff_mean REAL,
    spectral_contrast_mean REAL,

    mfcc_mean TEXT,  -- timbre
    mfcc_std TEXT

    --more could be added if need be

);

-- 3. CLAP audio embeddings
-- Stored as raw float32 bytes (512 x 4 = 2048 B).
--    Write:  emb.astype(np.float32).tobytes()
--    Read:   np.frombuffer(blob, dtype=np.float32)

CREATE TABLE IF NOT EXISTS clap_embeddings (
    song_id INTEGER NOT NULL REFERENCES songs(song_id) ON DELETE CASCADE,    
    model_name TEXT NOT NULL,
    dimension INTEGER NOT NULL DEFAULT 512,
    embedding BLOB NOT NULL,
    PRIMARY KEY (song_id, model_name)
);


-- 4. Human labels

-- Table of raters (our names or ids)
CREATE TABLE IF NOT EXISTS raters (
    rater_id  INTEGER PRIMARY KEY,
    name      TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS human_ratings (
    song_id INTEGER NOT NULL REFERENCES songs(song_id)  ON DELETE CASCADE,
    rater_id INTEGER NOT NULL REFERENCES raters(rater_id),
    energy REAL CHECK (energy BETWEEN 0 AND 1),
    happiness REAL CHECK (happiness BETWEEN 0 AND 1),
    chillness REAL CHECK (chillness BETWEEN 0 AND 1),
    coolness REAL CHECK (coolness BETWEEN 0 AND 1),
    warmth REAL CHECK (warmth BETWEEN 0 AND 1),
    danceability REAL CHECK (danceability BETWEEN 0 AND 1),

    PRIMARY KEY (song_id, rater_id)
);

-- Average of all ratings across raters
CREATE VIEW IF NOT EXISTS human_consensus AS
SELECT song_id,
       COUNT(*)          AS n_raters,
       AVG(energy)       AS energy,
       AVG(happiness)    AS happiness,
       AVG(chillness) AS chillness,
       AVG(coolness) AS coolness,
       AVG(warmth) AS warmth,
       AVG(danceability) AS danceability
FROM human_ratings
GROUP BY song_id;


-- 5. Model scores
-- A: CLAP, B: librosa, C: librosa and CLAP

CREATE TABLE IF NOT EXISTS song_scores (
    song_id INTEGER NOT NULL REFERENCES songs(song_id) ON DELETE CASCADE,
    system         TEXT    NOT NULL
                   CHECK (system IN ('A_clap_zeroshot', 'B_librosa', 'C_librosa_clap')),
    model_version  TEXT    NOT NULL DEFAULT 'v1',   -- e.g. 'ridge_v2', 'mlp_2026-11-20'
    energy         REAL CHECK (energy       BETWEEN 0 AND 1),
    happiness      REAL CHECK (happiness    BETWEEN 0 AND 1),
    chillness      REAL CHECK (chillness    BETWEEN 0 AND 1),
    coolness       REAL CHECK (coolness     BETWEEN 0 AND 1),
    warmth         REAL CHECK (warmth       BETWEEN 0 AND 1),
    danceability   REAL CHECK (danceability BETWEEN 0 AND 1),

    PRIMARY KEY (song_id, system, model_version)
);

-- 6. Tempo validation

CREATE TABLE IF NOT EXISTS tempo_checks (
    song_id     INTEGER NOT NULL REFERENCES songs(song_id) ON DELETE CASCADE,
    rater_id    INTEGER NOT NULL REFERENCES raters(rater_id),
    tapped_bpm  REAL    NOT NULL CHECK (tapped_bpm > 0),
    
    PRIMARY KEY (song_id, rater_id)
);


-- 7. Generated playlists

CREATE TABLE IF NOT EXISTS playlists (
    playlist_id     INTEGER PRIMARY KEY,
    photo_path      TEXT,
    target_minutes  REAL NOT NULL CHECK (target_minutes > 0),
    system          TEXT NOT NULL,                 -- which song_scores system was matched
    model_version   TEXT,
    energy          REAL,  -- the photo's Weather Report (after context adjustment)
    happiness       REAL,
    chillness       REAL,
    coolness        REAL,
    warmth          REAL,
    danceability    REAL
);
 
CREATE TABLE IF NOT EXISTS playlist_tracks (
    playlist_id  INTEGER NOT NULL REFERENCES playlists(playlist_id) ON DELETE CASCADE,
    position     INTEGER NOT NULL CHECK (position >= 1),
    song_id      INTEGER NOT NULL REFERENCES songs(song_id),
    similarity   REAL,                             -- cosine similarity to the photo
    PRIMARY KEY (playlist_id, position)
);

    
