"""SAM 3.1 cutouts for robot focus outlines (needs MODEL_API_KEY).

Segments the robot from each portrait PNG and saves boxes+masks to
assets/cutouts/<NAME>.json. The web client uses these for the selection
outline; without them it falls back to a plain ring highlight.
Segmentation is not 3D reconstruction — labeled as such in the UI.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.profiles import SAMPLES, CREATOR_TEMPLATE  # noqa: E402
from meta.adapters import sam_segment  # noqa: E402


def main():
    if not os.environ.get("MODEL_API_KEY"):
        print("GAP: MODEL_API_KEY not set. Cutouts skipped (ring fallback).")
        sys.exit(2)
    os.makedirs("assets/cutouts", exist_ok=True)
    for p in SAMPLES[:5] + [CREATOR_TEMPLATE]:
        src = "assets/portraits/%s.png" % p["name"]
        if not os.path.exists(src):
            print("missing %s — run make_portraits.py first" % src)
            continue
        try:
            res = sam_segment(src, "the robot")
        except Exception as e:  # noqa: BLE001
            print("%s: SAM call failed (%s) — shape conditional on guide" % (
                p["name"], e))
            continue
        with open("assets/cutouts/%s.json" % p["name"], "w") as f:
            json.dump(res, f)
        print("wrote assets/cutouts/%s.json" % p["name"])


if __name__ == "__main__":
    main()
