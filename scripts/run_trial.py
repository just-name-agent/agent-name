"""Seeded 7-day trial. Mock mode needs no key; spark mode needs MODEL_API_KEY."""
import argparse
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.profiles import SAMPLES, CREATOR_TEMPLATE, SYSTEM_PROMPT  # noqa: E402
from agents.runner import observe, decide  # noqa: E402
from engine.sim import new_state, run_day, metrics  # noqa: E402
from engine.store import connect, save_snapshot, record_run, export_run, log_hash  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--mode", choices=["mock", "spark"], default="mock")
    ap.add_argument("--out", default="demo/sample_run.json")
    ap.add_argument("--db", default="demo/trial.db")
    args = ap.parse_args()

    if args.mode == "spark" and not os.environ.get("MODEL_API_KEY"):
        print("MODEL_API_KEY not set — sim paused (quota rule), not battery death.")
        sys.exit(2)

    profiles = SAMPLES[:5] + [dict(CREATOR_TEMPLATE)]
    state = new_state(profiles, args.seed)
    rng = random.Random(args.seed)
    spark = None
    if args.mode == "spark":
        from meta.adapters import spark_decide
        profiles_by_name = {p["name"]: p for p in profiles}

        def spark(obs, profile):
            return spark_decide(
                obs, profile, SYSTEM_PROMPT.format(
                    name=profile["name"], value=profile["value"],
                    backstory=profile["backstory"], day=obs["day"],
                    battery=obs["battery"], stock=json.dumps(obs["stock"]),
                    trickles=obs["trickles"], grids=obs["grids"]))

    by_profile = {p["name"]: p for p in profiles}
    sources = {}
    for _ in range(args.days):
        decisions = {}
        for a in state["agents"]:
            if not a["alive"]:
                continue
            obs = observe(a, state, by_profile[a["name"]])
            d, src = decide(obs, by_profile[a["name"]], rng, spark)
            decisions[a["name"]] = d
            sources[src] = sources.get(src, 0) + 1
        run_day(state, decisions)

    m = metrics(state)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    cx = connect(args.db)
    save_snapshot(cx, args.seed, state["day"], state)
    record_run(cx, args.seed, args.mode, state, m)
    export_run(args.out, args.seed, args.mode, state, m)
    print("seed=%d mode=%s hash=%s metrics=%s sources=%s" % (
        args.seed, args.mode, log_hash(state), json.dumps(m), sources))
    print("wrote %s and %s" % (args.out, args.db))


if __name__ == "__main__":
    main()
