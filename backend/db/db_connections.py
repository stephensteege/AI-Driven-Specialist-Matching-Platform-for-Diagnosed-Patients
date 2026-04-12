from pathlib import Path
import sqlite3


PHYSICIAN_DB: Path = Path("./SurgeonsDatabase.sqlite")

# create a db connection check_same_thread allows for multiple threads
CONN: sqlite3.Connection = sqlite3.connect(PHYSICIAN_DB, check_same_thread=False)
CURSOR: sqlite3.Cursor = CONN.cursor()