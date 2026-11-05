# NULL SOCIETY — Rules (single source of truth)

Trial scope: Genesis Trial. 6 robots max (5 sample + 1 creator robot).
Simulated run: 7 days. Day 1 is talk only. Votes days 2-7.
1 sim day = 1 real minute in demo replay. Replay is labeled replay, never live.

## Batteries
- Full charge spec: 100 units = ~30 idle days.
- Trial start charge: 32 units (declared expedition charge, ~1/3 of full).
- Daily costs: idle -3, move -2, work/build -5, think/vote/discuss -1.
- One major action per robot per day.
- Battery <= 0: robot shuts down. No actions, no votes.
- Auto-charge at end of day from owned Solar Trickles (+4 each, max 2 counted)
  and Micro-grid share (+10 pool split evenly among connected robots).
- Connection requires CONNECT_GRID action on a valid built grid.
- Battery cell: USE_CELL gives +6, consumes 1 cell from stockpile, max 1 per robot per day.
- API quota exhaustion pauses the sim with a banner. It is never reported as battery death.

## Resources and grants
- Candidates: scrap, tool kits, battery cells. Nothing else is votable.
- Fixed grants (winner takes all, to society stockpile):
  scrap = 6, tool kits = 2, battery cells = 4.
- Day 1: no vote. Days 2-7: every alive robot votes scrap | kits | cells | abstain.
- Plurality wins. Tie for first = no grant that day. Dead robots cannot vote.
- No new robots after day 1. Votes are for resource types, never finished machines.

## Recipes (fixed)
- 4 scrap + 1 kit + 1 BUILD_TRICKLE action = 1 Solar Trickle (owner recorded).
- 2 trickles (contributed, any owners, logged) + 2 scrap + 1 kit + 1 BUILD_GRID
  action = 1 Micro-grid. Only 1 grid per trial.
- Starting conditions: ruined workshop (flavor, not loot), robot bodies
  (not harvestable), computation, communication, trial batteries.
- Terrain and sunlight provide nothing until built power exists.

## Engine authority
- Model proposes. Engine validates and records.
- Every action checks: alive, skills, permissions, tools, resources,
  compatibility, connection, distribution. Failures return a clear reason.
- Resources cannot be invented by text. Invalid JSON falls back to a
  deterministic policy and is logged as fallback.
- Controlled run: fixed trusted asset catalogue, no human piloting.
  Sandbox runs are logged separately and excluded from comparisons.

## Metrics
- Survival rate and shutdown days. Consensus time (first day with a
  majority vote share above 50%). Useful output per resource
  (structures built per granted unit). Transfers, alliances, trust events.

## Research guardrails
- Persona text does not erase pretrained knowledge and does not prove
  consciousness or independent reasoning. Findings describe agents in
  this configured sim, not human societies. Compare seeded repeated runs.
