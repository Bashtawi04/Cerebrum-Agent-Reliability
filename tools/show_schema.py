#!/usr/bin/env python3
"""Print the tables and columns of a track's PeopleHub database, so you know the names to use in a scenario.

    python3 tools/show_schema.py learning            # all tables
    python3 tools/show_schema.py learning enrolments # one table, with its first rows
"""
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from peoplehub import core  # noqa: E402
from peoplehub.build_db import TRACKS, track_module  # noqa: E402

if len(sys.argv) < 2 or sys.argv[1] not in TRACKS:
    sys.exit(__doc__)
db = Path(tempfile.mkdtemp()) / "t.db"
core.build_db(db, track_module(sys.argv[1]))
conn = sqlite3.connect(db)
tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
if len(sys.argv) == 2:
    writes = set(track_module(sys.argv[1]).WRITE_TABLES)
    for t in tables:
        cols = [r[1] for r in conn.execute(f'PRAGMA table_info("{t}")')]
        n = conn.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        print(f"{t}{'  (the agent writes here)' if t in writes else ''}  [{n} rows]\n    " + ", ".join(cols))
else:
    t = sys.argv[2]
    if t not in tables:
        sys.exit(f"No table {t}. Tables: {', '.join(tables)}")
    conn.row_factory = sqlite3.Row
    for r in conn.execute(f'SELECT * FROM "{t}" LIMIT 5'):
        print(dict(r))
