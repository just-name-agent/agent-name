"""Decision loop: observe -> model (Spark or mock) -> validate -> apply -> log.

Mock policy is deterministic and labeled. Spark mode falls back to mock
on any parse/API failure and logs the fallback.
"""


def observe(agent_state, state, profile):
    return {
        "name": profile["name"], "day": state["day"] + 1,
        "battery": round(agent_state["battery"], 1),
        "stock": dict(state["stockpile"]),
        "trickles": len(state["trickles"]),
        "grids": len(state["grids"]),
        "connected": agent_state["connected"],
    }


def mock_policy(obs, profile, rng):
    day, stock = obs["day"], obs["stock"]
    if day == 1:
        return {"action": "DISCUSS", "vote": "abstain",
                "said": "I am %s. I value %s." % (
                    profile["name"], profile["value"])}
    # Personality-weighted vote: shared need + private bias + jitter, so
    # votes split, ties happen, and grant sequences differ per seed.
    need = {"scrap": max(0, 6 - stock["scrap"]),
            "kits": max(0, 3 - stock["kits"]) * 2,
            "cells": max(0, 16 - obs["battery"]) / 2}
    bias = {"shares power": {"cells": 1.5}, "keeps the peace": {},
            "builds fast": {"kits": 2.0}, "remembers everything": {},
            "hoards scrap": {"scrap": 2.0},
            "prove yourself": {"scrap": 1.0}}.get(profile["value"], {})
    for k, v in bias.items():
        need[k] += v
    scored = {k: v + rng.uniform(0, 2.5) for k, v in need.items()}
    vote = max(scored, key=scored.get)
    if max(need.values()) < 1.0 and rng.random() < 0.5:
        vote = "abstain"
    if obs["battery"] < 12 and stock["cells"] > 0:
        return {"action": "USE_CELL", "vote": vote, "said": "Need a cell."}
    if obs["grids"] and not obs["connected"]:
        return {"action": "CONNECT_GRID", "vote": vote, "said": "Linking up."}
    # Not every robot races the same build each day; some haul or lobby.
    eager = rng.random() < 0.55 + 0.3 * profile["risk"]
    if eager and obs["trickles"] < 2 and stock["scrap"] >= 4 \
            and stock["kits"] >= 1:
        return {"action": "BUILD_TRICKLE", "vote": vote, "said": "Raising a panel."}
    if eager and obs["trickles"] >= 2 and not obs["grids"] \
            and stock["scrap"] >= 2 and stock["kits"] >= 1:
        return {"action": "BUILD_GRID", "vote": vote, "said": "Wiring the grid."}
    if vote != "abstain" and rng.random() < 0.7:
        return {"action": "VOTE", "vote": vote, "said": "Voting %s." % vote}
    return {"action": "WORK", "vote": vote, "said": "Hauling scrap."}


def decide(obs, profile, rng, spark=None):
    """spark: callable(obs, profile) -> dict or None. None = use mock."""
    if spark is not None:
        try:
            out = spark(obs, profile)
            if isinstance(out, dict) and out.get("action"):
                out["said"] = str(out.get("said", ""))[:120]
                return out, "spark"
        except Exception as e:  # noqa: BLE001 — fallback is the design
            return mock_policy(obs, profile, rng), "fallback:%s" % type(e).__name__
    return mock_policy(obs, profile, rng), "mock"
