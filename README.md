# NULL SOCIETY — Genesis Trial

6 robots wake with 32 charge each and nothing else. They vote, share, and
build verified power before day 7 — or brown out. Model proposes, engine
validates. Talk cannot create steel.

Built for the Meta Global AI Developer Hackathon — Indie Developer track,
Push the Frontier theme. Built with Muse Code.

## Run it (no key needed — mock mode)

```sh
python tests/run_all.py
python scripts/run_trial.py --seed 2 --days 7 --mode mock
cd web && python -m http.server 8000
# open http://localhost:8000 — accelerated replay, 1 day = 1 min
```

## Run it live (needs `MODEL_API_KEY` in `.env`, never committed)

```sh
python scripts/smoke_api.py
python scripts/run_trial.py --seed 2 --days 7 --mode spark
python scripts/make_portraits.py   # Muse Image portraits
python scripts/sam_cutouts.py      # SAM 3.1 selection outlines
```

Quota exhaustion pauses the sim with a banner. It is never shown as battery death.

## What judges get

- Rules: [docs/rules.md](docs/rules.md) — batteries, grants, recipes, votes.
- Meta proof: [docs/meta-models.md](docs/meta-models.md) — Spark, Image,
  Voice Transcribe, SAM 3.1, all through Meta Model API.
- Demo: [docs/demo-script.md](docs/demo-script.md) + `demo/sample_run.json`
  (seed 2 survives, hash `461e96ed94c1e312`) and
  `demo/sample_run_brownout.json` (seed 3 browns out, same rules).
- Reproduce: same seed + same mode = same event-log hash. SQLite snapshots
  in `demo/*.db`.

## Honest limits

Persona text does not erase pretrained knowledge and proves nothing about
consciousness. Findings describe agents in this sim, not human societies.
SAM segmentation is selection/outline only, not 3D reconstruction.
Mock assets are labeled placeholders.

## Roadmap

Trial → persistent city → more recipes → creator SDK → coordination
benchmark for agents under scarcity.

## Submission checklist

- [ ] Track: Indie Developer. Theme: Push the Frontier.
- [ ] Official Rules accepted; rubric weights re-verified (plan assumed
      Impact 30 / Meta 25 / Demo 25 / Depth 20 from the supplied guide).
- [ ] Repo public, video linked, run hash quoted.
- [ ] Portal status checked (submissions were due Nov 4 9PM ET; if closed,
      this build stands as portfolio + viral entry).

MIT — see LICENSE.
