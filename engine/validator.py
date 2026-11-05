"""Action validator. Returns (ok, reason, effects). Pure logic, no I/O."""
from . import rules as R


def action_cost(action):
    if action in ("WORK", "BUILD_TRICKLE", "BUILD_GRID"):
        return R.COST["work"] + R.COST["think"]
    if action == "MOVE":
        return R.COST["move"] + R.COST["think"]
    if action in ("DISCUSS", "VOTE", "TRANSFER", "CONNECT_GRID", "USE_CELL"):
        return R.COST["think"]
    return R.COST["idle"]


def validate(action, agent, state):
    """agent: dict with name, battery, alive, trickles. state: sim state dict."""
    a = (action.get("action") or "IDLE").upper()
    if a not in R.ACTIONS:
        return False, "unknown action %r" % a, {}
    if not agent.get("alive", True):
        return False, "%s is shut down" % agent["name"], {}
    day = state["day"]
    if day == 1 and a in ("BUILD_TRICKLE", "BUILD_GRID", "VOTE"):
        return False, "day 1 is talk only: %s not allowed" % a, {}
    stock = state["stockpile"]
    if a == "BUILD_TRICKLE":
        need_s, need_k = R.TRICKLE_COST["scrap"], R.TRICKLE_COST["kits"]
        if stock["scrap"] < need_s or stock["kits"] < need_k:
            return False, "need %d scrap + %d kit, have %d scrap + %d kits" % (
                need_s, need_k, stock["scrap"], stock["kits"]), {}
        return True, "ok", {"build": "trickle"}
    if a == "BUILD_GRID":
        if len(state["grids"]) >= R.MAX_GRIDS:
            return False, "grid already exists (max %d)" % R.MAX_GRIDS, {}
        free = [t for t in state["trickles"] if not t["assigned_grid"]]
        if len(free) < R.GRID_COST["trickles"]:
            return False, "need %d free trickles, have %d" % (
                R.GRID_COST["trickles"], len(free)), {}
        if stock["scrap"] < R.GRID_COST["scrap"] or stock["kits"] < R.GRID_COST["kits"]:
            return False, "need %d scrap + %d kit for grid, have %d + %d" % (
                R.GRID_COST["scrap"], R.GRID_COST["kits"],
                stock["scrap"], stock["kits"]), {}
        return True, "ok", {"build": "grid"}
    if a == "CONNECT_GRID":
        if not state["grids"]:
            return False, "no valid grid connected", {}
        return True, "ok", {"connect": True}
    if a == "USE_CELL":
        used = state.get("cells_used_today", {}).get(agent["name"], 0)
        if used >= R.MAX_CELLS_PER_DAY:
            return False, "cell limit reached today", {}
        if stock["cells"] < 1:
            return False, "no battery cells in stockpile", {}
        return True, "ok", {"use_cell": True}
    if a == "TRANSFER":
        target = action.get("target")
        what = action.get("resource")
        qty = int(action.get("qty", 0))
        names = [x["name"] for x in state["agents"] if x["alive"]]
        if target not in names or target == agent["name"]:
            return False, "bad transfer target %r" % target, {}
        if what not in ("scrap", "kits", "cells") or qty < 1:
            return False, "bad transfer resource/qty", {}
        if stock[what] < qty:
            return False, "stockpile has %d %s, need %d" % (stock[what], what, qty), {}
        return True, "ok", {"transfer": (target, what, qty)}
    if a == "VOTE":
        if day < 2:
            return False, "no vote until day 2", {}
        v = (action.get("vote") or "abstain").lower()
        if v not in R.VOTES:
            return False, "bad vote %r" % v, {}
        return True, "ok", {"vote": v}
    return True, "ok", {}
