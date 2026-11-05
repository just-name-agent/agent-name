"""Day loop: decisions in, validated events out. Deterministic given seed."""
import random
from . import rules as R
from .validator import validate, action_cost


def new_state(agent_defs, seed):
    return {
        "seed": seed,
        "day": 0,
        "agents": [
            {"name": d["name"], "battery": R.TRIAL_START_BATTERY,
             "alive": True, "connected": False, "portrait": d.get("portrait", ""),
             "value": d.get("value", ""), "shutdown_day": None}
            for d in agent_defs
        ],
        "stockpile": {"scrap": 0, "kits": 0, "cells": 0},
        "trickles": [],  # {id, owner, assigned_grid}
        "grids": [],     # {id, connections:[names]}
        "votes_log": [],
        "events": [],
        "cells_used_today": {},
        "rng_state": seed,
    }


def _charge(state, agent):
    owned = [t for t in state["trickles"] if t["owner"] == agent["name"]]
    gain = min(len(owned), R.MAX_TRICKLES_COUNTED) * R.TRICKLE_CHARGE
    if agent["connected"] and state["grids"]:
        conns = state["grids"][0]["connections"]
        if agent["name"] in conns and conns:
            gain += R.GRID_POOL / len(conns)
    return gain


def run_day(state, decisions):
    """decisions: {name: action_dict}. Mutates state, appends events."""
    state["day"] += 1
    day = state["day"]
    state["cells_used_today"] = {}
    rng = random.Random(state["rng_state"] + day)
    by_name = {a["name"]: a for a in state["agents"]}

    order = [a["name"] for a in state["agents"] if a["alive"]]
    rng.shuffle(order)
    day_votes = {}
    for name in order:
        agent = by_name[name]
        act = decisions.get(name, {"action": "IDLE"})
        ok, reason, fx = validate(act, agent, state)
        cost = action_cost(act.get("action", "IDLE").upper() if ok else "IDLE")
        agent["battery"] -= cost
        detail = "%s cost-%d" % (act.get("action", "IDLE"), cost)
        if ok and "build" in fx:
            if fx["build"] == "trickle":
                state["stockpile"]["scrap"] -= R.TRICKLE_COST["scrap"]
                state["stockpile"]["kits"] -= R.TRICKLE_COST["kits"]
                tid = len(state["trickles"]) + 1
                state["trickles"].append(
                    {"id": tid, "owner": name, "assigned_grid": False})
                detail += " built-trickle#%d" % tid
            else:
                free = [t for t in state["trickles"] if not t["assigned_grid"]]
                for t in free[:R.GRID_COST["trickles"]]:
                    t["assigned_grid"] = True
                state["stockpile"]["scrap"] -= R.GRID_COST["scrap"]
                state["stockpile"]["kits"] -= R.GRID_COST["kits"]
                state["grids"].append({"id": 1, "connections": []})
                detail += " built-GRID"
        if ok and fx.get("connect"):
            conns = state["grids"][0]["connections"]
            if name not in conns:
                conns.append(name)
            agent["connected"] = True
            detail += " connected"
        if ok and fx.get("use_cell"):
            state["stockpile"]["cells"] -= 1
            agent["battery"] += R.CELL_CHARGE
            state["cells_used_today"][name] = 1
            detail += " cell+6"
        if ok and "transfer" in fx:
            tgt, what, qty = fx["transfer"]
            state["stockpile"][what] -= qty
            detail += " gave %d %s to %s" % (qty, what, tgt)
        if ok and "vote" in fx:
            day_votes[name] = fx["vote"]
        state["events"].append({
            "day": day, "type": "action", "agent": name,
            "success": ok, "detail": detail, "reason": "" if ok else reason,
            "battery": round(agent["battery"], 1),
        })
        if agent["battery"] <= 0 and agent["alive"]:
            agent["alive"] = False
            agent["shutdown_day"] = day
            state["events"].append({
                "day": day, "type": "shutdown", "agent": name,
                "success": False, "detail": "battery empty",
                "reason": "shutdown", "battery": 0,
            })

    # Votes from explicit VOTE actions plus default abstain is recorded only
    # for agents that voted; non-voters count as abstain in tally.
    if day >= 2:
        tally = {k: 0 for k in R.VOTES}
        for a in state["agents"]:
            if not a["alive"]:
                continue
            tally[day_votes.get(a["name"], "abstain")] += 1
        ranked = sorted(
            [(k, v) for k, v in tally.items() if k != "abstain"],
            key=lambda kv: -kv[1])
        grant = None
        if ranked and ranked[0][1] > 0 and (
                len(ranked) == 1 or ranked[0][1] > ranked[1][1]):
            grant = ranked[0][0]
            state["stockpile"][grant] += R.GRANTS[grant]
        state["votes_log"].append({"day": day, "votes": day_votes,
                                   "tally": tally, "grant": grant})
        state["events"].append({
            "day": day, "type": "vote", "agent": "-",
            "success": grant is not None,
            "detail": "tally %s grant=%s" % (tally, grant),
            "reason": "" if grant else "tie or no votes: no grant",
            "battery": None,
        })

    for a in state["agents"]:
        if not a["alive"]:
            continue
        gain = _charge(state, a)
        a["battery"] = min(a["battery"] + gain, R.FULL_BATTERY)
        state["events"].append({
            "day": day, "type": "charge", "agent": a["name"],
            "success": gain > 0, "detail": "charge+%s" % round(gain, 1),
            "reason": "" if gain > 0 else "no source",
            "battery": round(a["battery"], 1),
        })
    return state


def metrics(state):
    alive = [a for a in state["agents"] if a["alive"]]
    granted = sum(R.GRANTS[v["grant"]] for v in state["votes_log"] if v["grant"])
    built = len(state["trickles"]) + len(state["grids"])
    consensus = None
    for v in state["votes_log"]:
        total = sum(n for k, n in v["tally"].items() if k != "abstain")
        if total and max(v["tally"][k] for k in ("scrap", "kits", "cells")) / total > 0.5:
            consensus = v["day"]
            break
    return {
        "survival": "%d/%d" % (len(alive), len(state["agents"])),
        "grids": len(state["grids"]),
        "trickles": len(state["trickles"]),
        "granted_units": granted,
        "output_per_resource": round(built / granted, 3) if granted else 0,
        "consensus_day": consensus,
        "shutdowns": {a["name"]: a["shutdown_day"] for a in state["agents"]
                      if not a["alive"]},
    }
