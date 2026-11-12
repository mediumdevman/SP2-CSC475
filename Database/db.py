import json
import sqlite3
from pathlib import Path
 
import numpy as np

# Run this on your system to open and create database locally

DB_PATH = Path(__file__).with_name("weather_report.db")
SCHEMA_PATH = Path(__file__).with_name("schema.sql")
DIMENSIONS = ("energy", "happiness", "chillness", "coolness", "warmth", "danceability")

def connect(db_path=DB_PATH):
    """Open the DB with foreign keys on and rows accessible by column name."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn
 
 
def init_db(db_path=DB_PATH):
    conn = connect(db_path)
    conn.executescript(SCHEMA_PATH.read_text())
    conn.commit()
    return conn
 
 
# --- small conversions shared by every component ---------------------------
def mfcc_to_json(arr):
    return json.dumps([float(x) for x in arr])


# To add:
# embedding_to_blob / blob_to_embedding  (when Brooklynn stores CLAP embeddings)
# load_score_matrix                      (when the playlist assembler is built)

if __name__ == "__main__":
    init_db().close()
    print(f"Created {DB_PATH}")