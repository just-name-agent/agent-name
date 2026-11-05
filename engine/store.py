"""Persistence: SQLite snapshots + JSON event log. Stdlib only."""
import hashlib
import json
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS snapshots (
  seed INTEGER, day INTEGER, state_json TEXT,
  PRIMARY KEY (seed, day));
CREATE TABLE IF NOT EXISTS runs (
  seed INTEGER PRIMARY KEY, mode TEXT, log_hash TEXT, metrics_json TEXT);
"""


def connect(path):
    cx = sqlite3.connect(path)
    cx.executescript(SCHEMA)
    return cx


def save_snapshot(cx, seed, day, state):
    cx.execute("INSERT OR REPLACE INTO snapshots VALUES (?,?,?)",
               (seed, day, json.dumps(state, sort_keys=True)))
    cx.commit()


def log_hash(state):
    blob = json.dumps(state["events"], sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


def record_run(cx, seed, mode, state, metrics):
    cx.execute("INSERT OR REPLACE INTO runs VALUES (?,?,?,?)",
               (seed, mode, log_hash(state), json.dumps(metrics, sort_keys=True)))
    cx.commit()


def export_run(path, seed, mode, state, metrics):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"seed": seed, "mode": mode, "metrics": metrics,
                   "votes_log": state["votes_log"], "events": state["events"],
                   "agents": state["agents"], "stockpile": state["stockpile"],
                   "trickles": state["trickles"], "grids": state["grids"]},
                  f, indent=1)
