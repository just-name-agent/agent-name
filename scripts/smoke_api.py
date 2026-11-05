"""One live call per model. Needs MODEL_API_KEY. Fails closed with a clear gap."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from meta.adapters import (  # noqa: E402
    spark_decide, generate_image, SPARK, IMAGE, TRANSCRIBE, SAM)


def main():
    if not os.environ.get("MODEL_API_KEY"):
        print("GAP: MODEL_API_KEY not set. Live verification pending.")
        print("Set it in .env (never commit) and rerun.")
        sys.exit(2)
    obs = {"name": "PROBE", "day": 2, "battery": 30,
           "stock": {"scrap": 0, "kits": 0, "cells": 0},
           "trickles": 0, "grids": 0, "connected": False}
    try:
        d = spark_decide(obs, {"name": "PROBE", "value": "probe",
                               "backstory": "smoke test"},
                         "Reply with ONE JSON object only: "
                         '{"action":"VOTE","vote":"scrap"}.')
        print("spark %s: OK action=%s" % (SPARK, d.get("action")))
    except Exception as e:  # noqa: BLE001
        print("spark %s: FAIL %s" % (SPARK, e))
    try:
        generate_image("pixel robot portrait, front view, plain background")
        print("image %s: OK" % IMAGE)
    except Exception as e:  # noqa: BLE001
        print("image %s: FAIL %s" % (IMAGE, e))
    print("voice %s: needs audio file — run with --audio to test transcribe" % TRANSCRIBE)
    print("sam %s: request shape conditional on media-segmentation guide" % SAM)


if __name__ == "__main__":
    main()
