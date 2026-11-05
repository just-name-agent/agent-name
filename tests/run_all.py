"""Plain-python test runner. No installs. Fails loud on first error."""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.profiles import SAMPLES  # noqa: E402
from agents.runner import observe, mock_policy  # noqa: E402
from engine.sim import new_state, run_day, metrics  # noqa: E402
from engine.store import log_hash  # noqa: E402
from engine.validator import validate  # noqa: E402

PASS = []


def check(name, cond, extra=""):
    if not cond:
        raise AssertionError("FAIL %s %s" % (name, extra))
    PASS.append(name)


def t_energy_math():
    s = new_state(SAMPLES[:2], 1)
    a = s["agents"][0]
    before = a["battery"]
    run_day(s, {a["name"]: {"action": "WORK"}})
    check("energy-work-costs", a["battery"] < before, a["battery"])


def t_rejects_without_tools():
    s = new_state(SAMPLES[:2], 1)
    s["day"] = 2
    ok, reason, _ = validate({"action": "BUILD_TRICKLE"}, s["agents"][0], s)
    check("reject-no-stock", not ok and "need" in reason, reason)


def t_rejects_grid_without_trickles():
    s = new_state(SAMPLES[:2], 1)
    s["day"] = 2
    s["stockpile"] = {"scrap": 9, "kits": 9, "cells": 0}
    ok, reason, _ = validate({"action": "BUILD_GRID"}, s["agents"][0], s)
    check("reject-no-trickles", not ok and "trickle" in reason, reason)


def t_rejects_connect_without_grid():
    s = new_state(SAMPLES[:2], 1)
    s["day"] = 2
    ok, reason, _ = validate({"action": "CONNECT_GRID"}, s["agents"][0], s)
    check("reject-no-grid", not ok and "grid" in reason, reason)


def t_day1_talk_only():
    s = new_state(SAMPLES[:2], 1)
    s["day"] = 1
    ok, _, _ = validate({"action": "VOTE", "vote": "scrap"}, s["agents"][0], s)
    check("day1-no-vote", not ok)


def t_tie_no_grant():
    s = new_state(SAMPLES[:2], 1)
    s["day"] = 1
    run_day(s, {s["agents"][0]["name"]: {"action": "VOTE", "vote": "scrap"},
                s["agents"][1]["name"]: {"action": "VOTE", "vote": "kits"}})
    check("tie-no-grant", s["votes_log"][-1]["grant"] is None,
          s["votes_log"][-1])


def t_dead_cannot_vote():
    s = new_state(SAMPLES[:2], 1)
    s["day"] = 1
    s["agents"][0]["alive"] = False
    run_day(s, {s["agents"][1]["name"]: {"action": "VOTE", "vote": "cells"}})
    check("dead-novote", s["votes_log"][-1]["tally"]["cells"] == 1)


def t_trickle_then_grid():
    s = new_state(SAMPLES[:6] if len(SAMPLES) >= 6 else SAMPLES[:5], 1)
    s["day"] = 1
    s["stockpile"] = {"scrap": 20, "kits": 6, "cells": 4}
    n0, n1 = s["agents"][0]["name"], s["agents"][1]["name"]
    run_day(s, {n0: {"action": "BUILD_TRICKLE"}, n1: {"action": "BUILD_TRICKLE"}})
    check("two-trickles", len(s["trickles"]) == 2, len(s["trickles"]))
    run_day(s, {n0: {"action": "BUILD_GRID"}})
    check("grid-built", len(s["grids"]) == 1)
    run_day(s, {n0: {"action": "CONNECT_GRID"}})
    check("grid-connect", n0 in s["grids"][0]["connections"])


def t_replay_hash_stable():
    def run_once():
        s = new_state(SAMPLES[:5], 7)
        rng = random.Random(7)
        prof = {p["name"]: p for p in SAMPLES[:5]}
        for _ in range(7):
            ds = {}
            for a in s["agents"]:
                if a["alive"]:
                    ds[a["name"]] = mock_policy(
                        observe(a, s, prof[a["name"]]), prof[a["name"]], rng)
            run_day(s, ds)
        return log_hash(s), metrics(s)
    h1, _ = run_once()
    h2, m2 = run_once()
    check("replay-stable", h1 == h2, (h1, h2))
    check("metrics-shape", "survival" in m2 and "consensus_day" in m2, m2)


if __name__ == "__main__":
    fns = [(k, v) for k, v in globals().items() if k.startswith("t_")]
    for _, fn in sorted(fns):
        fn()
    print("PASS %d/%d: %s" % (len(PASS), len(PASS), ", ".join(sorted(PASS))))
