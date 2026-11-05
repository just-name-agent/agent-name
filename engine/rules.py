"""Locked trial constants. Mirrors docs/rules.md — edit both together."""

TRIAL_DAYS = 7
MAX_ROBOTS = 6
FULL_BATTERY = 100
TRIAL_START_BATTERY = 32

COST = {"idle": 3, "move": 2, "work": 5, "think": 1}
TRICKLE_CHARGE = 4
MAX_TRICKLES_COUNTED = 2
GRID_POOL = 10
CELL_CHARGE = 6
MAX_CELLS_PER_DAY = 1

GRANTS = {"scrap": 6, "kits": 2, "cells": 4}
TRICKLE_COST = {"scrap": 4, "kits": 1}
GRID_COST = {"scrap": 2, "kits": 1, "trickles": 2}
MAX_GRIDS = 1

ACTIONS = (
    "IDLE", "MOVE", "WORK", "DISCUSS", "VOTE",
    "BUILD_TRICKLE", "BUILD_GRID", "CONNECT_GRID",
    "TRANSFER", "USE_CELL",
)
VOTES = ("scrap", "kits", "cells", "abstain")
